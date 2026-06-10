import random


class All_InBot:
    """
    Kuhn Poker bot for the All_In team. Design goal: a "balanced robust"
    strategy that is near-unexploitable against strong opponents while still
    punishing weak/passive ones.

    Why this shape, and not a pure exploiter:
      Kuhn Poker is solved. A Nash-equilibrium (NE) strategy is UNEXPLOITABLE -
      no opponent can beat it (best case for them is break-even). The flip side
      is that NE only wins tiny margins from weak bots. A pure maximal exploiter
      crushes weak bots but is itself wildly exploitable and LOSES to a strong
      best-responder. So we do both:
        * Baseline = exact NE (alpha = 1/3). This is the unexploitable floor:
          against any opponent (including an equilibrium or counter-exploiting
          bot) it stays around break-even and is never crushed.
        * On top of NE we layer EVIDENCE-GATED, BOUNDED deviations that exploit
          opponents only along axes we can actually observe, with conservative
          triggers and capped magnitudes so worst-case regret stays small.

    What is observable (and what is not):
      The engine only calls us at our own decision nodes and never reveals the
      result of a hand, so we can never see our own win/loss feedback nor the
      opponent's response to OUR bets (those nodes are terminal). We can only
      observe two opponent frequencies:
        - open_rate : P(opponent bets | opponent is P1)         [seen as P2]
        - raise_rate: P(opponent bets | we checked as P1)       [deferred read]
      A NE opponent's open_rate/raise_rate top out around 0.444, so a rate
      meaningfully above that proves the opponent over-bets (so we widen our
      bluff-catches), while a mid-range opener that bets its strong hands but
      folds its weak ones is one we can bluff (see the band gate below).

    Decision nodes (from engine.py):
      ''   - we are P1, opening
      'p'  - we are P2, opponent checked to us
      'b'  - we are P2, opponent bet into us
      'pb' - we are P1, we checked and the opponent raised
    """

    # --- Nash-equilibrium baseline (alpha = 1/3), the unexploitable floor. ---
    _A = 1.0 / 3.0
    NE = {
        ('J', ''):   _A,           # bluff-open J at the NE rate
        ('Q', ''):   0.0,          # never open Q
        ('K', ''):   1.0,          # always value-bet K (3*alpha = 1)
        ('J', 'p'):  1.0 / 3.0,    # P2 bluff J vs a check
        ('Q', 'p'):  0.0,          # P2 checks Q back
        ('K', 'p'):  1.0,          # P2 value-bets K
        ('J', 'b'):  0.0,          # fold J to a bet (J can never win a showdown)
        ('Q', 'b'):  1.0 / 3.0,    # bluff-catch Q at the NE rate
        ('K', 'b'):  1.0,          # always call K
        ('J', 'pb'): 0.0,          # fold J to a raise
        ('Q', 'pb'): 2.0 / 3.0,    # call Q vs a raise at NE rate (alpha + 1/3)
        ('K', 'pb'): 1.0,          # always call K
    }

    # --- Exploitation tuning (deviations from NE) ---
    MIN_SAMPLES = 40          # min decayed observations before trusting a stat
    DECAY = 0.99              # tracks the CURRENT opponent (arena reuses one
                              # instance across matches; decay sheds stale data)

    # A J-bluff is only profitable against an honest value-bettor that folds
    # its weak hands. Such an opener BETS its strong hand (K) -> open_rate near
    # ~1/3, NOT near 0. A trapper/counter-exploiter that punishes bluffs instead
    # CHECKS its strong hands -> open_rate near 0. So we bluff J only when the
    # opener's aggression sits in the "honest" band: above a trapper, below NE.
    # Lower bound excludes a trapper (open_rate ~ 0 means it slow-plays its
    # strong hands and will snap our bluffs). Upper bound excludes a
    # calling-station/maniac (very high open_rate means it also calls our
    # bluffs). In between, bluffing the J-steal is +EV vs folders and exactly
    # break-even vs a Nash opponent (NE calls just enough to make us
    # indifferent), so the wide band is safe.
    OPEN_BAND_LO = 0.25
    OPEN_BAND_HI = 0.60
    # P1 J-open and P2 J-steal are observationally indistinguishable bets: an
    # honest folder (e.g. DefaultBot) and a disguised bluff-catcher both open K
    # only, so we cannot tell who folds to our bet. We therefore keep these
    # deviations MODERATE so the upside vs folders stays large while the
    # worst-case loss vs a hidden bluff-catcher stays bounded. The P2 steal has
    # a far better reward/risk ratio (+2 vs a folder, -1 vs a caller) than the
    # P1 open (+0.5 vs -1), so the P1 open stays at the NE rate.
    EXPLOIT_J_OPEN = 1.0 / 3.0   # = NE: P1 J-open deviation disabled (poor R/R)
    EXPLOIT_J_STEAL = 0.90       # P2 J-bluff frequency inside the honest band

    CALL_OPEN = 0.55          # open_rate above this => widen Q bluff-catches
    MANIAC_OPEN = 0.80        # open_rate at/above which we always call Q
    CALL_RAISE = 0.55         # raise_rate above this => widen Q calls vs raise
    MANIAC_RAISE = 0.85       # raise_rate at/above which we always call Q

    def __init__(self):
        self.name = "All_In"

        # Decaying weighted counts of the two observable opponent frequencies.
        self.open_bet_w = 0.0
        self.open_tot_w = 0.0
        self.raise_bet_w = 0.0
        self.raise_tot_w = 0.0

        # True iff our previous action was a P1 check at '' whose outcome we
        # have not yet attributed to the opponent.
        self._pending_p1_check = False

    def _open_rate(self):
        if self.open_tot_w < self.MIN_SAMPLES:
            return None
        return self.open_bet_w / self.open_tot_w

    def _raise_rate(self):
        if self.raise_tot_w < self.MIN_SAMPLES:
            return None
        return self.raise_bet_w / self.raise_tot_w

    def _observe(self, state) -> None:
        """Update the decaying opponent model from observable information."""
        h = state.history

        self.open_bet_w *= self.DECAY
        self.open_tot_w *= self.DECAY
        self.raise_bet_w *= self.DECAY
        self.raise_tot_w *= self.DECAY

        # Resolve a pending P1 check: if this same hand continued to 'pb' the
        # opponent raised; any other history means the prior hand ended 'pp'
        # (opponent checked back) and a new hand has begun.
        if self._pending_p1_check:
            self.raise_tot_w += 1.0
            if h == 'pb':
                self.raise_bet_w += 1.0
            self._pending_p1_check = False

        # When we are P2, the single-character history is the opponent's open.
        if len(h) == 1:
            self.open_tot_w += 1.0
            if h == 'b':
                self.open_bet_w += 1.0

    @staticmethod
    def _ramp(x, lo, hi, base, top):
        """Linearly interpolate from base at x=lo to top at x>=hi."""
        if x <= lo:
            return base
        if x >= hi:
            return top
        return base + (top - base) * (x - lo) / (hi - lo)

    def _bet_probability(self, card: str, history: str) -> float:
        p = self.NE[(card, history)]
        open_rate = self._open_rate()
        raise_rate = self._raise_rate()
        bluffable = (open_rate is not None
                     and self.OPEN_BAND_LO < open_rate < self.OPEN_BAND_HI)

        # --- Bounded bluff exploitation vs an observably honest opener. ---
        # Only J is ever bluffed beyond NE: betting Q is dominated, and the
        # band gate keeps us from bluffing into a trapper (open_rate ~ 0) or an
        # equilibrium/aggressive bot (open_rate >= ~0.44).
        if bluffable:
            if (card, history) == ('J', ''):
                return self.EXPLOIT_J_OPEN
            if (card, history) == ('J', 'p'):
                return self.EXPLOIT_J_STEAL

        # --- Safe bluff-catch exploitation vs an observable over-bettor. ---
        # Only widens Q calls (J can never win a showdown, K already calls).
        # Triggers only above the NE ceiling (~0.444), so it never fires
        # against an equilibrium opponent.
        if (card, history) == ('Q', 'b') and open_rate is not None:
            return self._ramp(open_rate, self.CALL_OPEN, self.MANIAC_OPEN,
                              self.NE[('Q', 'b')], 1.0)
        if (card, history) == ('Q', 'pb') and raise_rate is not None:
            return self._ramp(raise_rate, self.CALL_RAISE, self.MANIAC_RAISE,
                              self.NE[('Q', 'pb')], 1.0)

        return p

    def get_action(self, state) -> str:
        self._observe(state)

        p_bet = self._bet_probability(state.my_card, state.history)
        action = 'b' if random.random() < p_bet else 'p'

        # Arm the deferred observer if we just checked as the opener.
        if state.history == '' and action == 'p':
            self._pending_p1_check = True

        return action
