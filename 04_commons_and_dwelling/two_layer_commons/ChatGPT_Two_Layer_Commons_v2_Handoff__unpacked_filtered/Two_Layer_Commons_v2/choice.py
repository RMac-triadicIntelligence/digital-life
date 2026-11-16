"""Momentary choices consume only made-available outcomes and signed shape."""

from collections import deque

DECISION_CAPACITY = 12


class Choice:
    def __init__(self, mode):
        self.mode = mode
        self.interpretation = None
        self.case = None
        self.observations = {}
        self.decisions = deque(maxlen=DECISION_CAPACITY)

    def snapshot(self):
        return {
            "interpretation": self.interpretation,
            "current_case": self.case,
            "source_values": dict(self.observations),
            "decision_topics": list(self.decisions),
        }

    def pick(self, topic, scores, shape, **reason):
        if self.mode != "ACTIVE":
            raise RuntimeError("member policy invoked outside active choice")
        selected = max(scores, key=scores.__getitem__)
        decision = {"topic": topic, "options": list(scores), "selected": selected,
                    "scores": {option: round(score, 6) for option, score in scores.items()},
                    "signed_character": shape.snapshot(), "basis": reason, "origin": "member"}
        self.decisions.append(topic)
        return decision

    def default(self, topic, options, action):
        return {"topic": topic, "options": list(options), "selected": action,
                "scores": None, "signed_character": None, "basis": {"default": action},
                "origin": "frozen_default"}

    def ask_story(self, shape):
        return self.pick("history.story_request",
                         {"wait": 0.64, "ask": shape.curiosity + 0.13 * shape.formality},
                         shape, public_invitation=True)

    def read_story(self, story_bytes, shape):
        text = story_bytes.decode("utf-8")
        # Literal cue extraction. The reader neither receives a tag about truth
        # nor knows any source's result for a later evidence case.
        lines = text.lower().split(".")
        shared_origin = any("both cords" in line and "one watchman" in line for line in lines)
        alternative = any("second watchman" in line for line in lines)
        scores = {"hold_meaning_open": 0.29, "notice_watchman": 0.64 + 0.05 * shape.formality,
                  "check_source_independence": 0.14 + 0.68 * shape.curiosity}
        if shared_origin and alternative:
            scores["check_source_independence"] += 0.10
        else:
            del scores["check_source_independence"]
        decision = self.pick("history.interpret_story", scores, shape,
                             text_cues={"shared_origin": shared_origin, "another_watchman": alternative})
        self.interpretation = decision["selected"]
        return decision

    def evidence_action(self, shape, sensation, permissions, command):
        options = ["wait", "check_repeat"]
        if sensation.independent_available:
            options.append("check_independent")
        if self.mode == "BODY_ONLY":
            return None
        if self.mode == "FROZEN":
            return self.default("thought.seek", options, "check_repeat")
        concern = self.interpretation == "check_source_independence"
        facet, world = permissions.facet_hold, permissions.world_hold
        scarce = sensation.short and not sensation.carried
        scores = {
            "wait": 0.20 + 0.65 * scarce + 0.10 * world,
            "check_repeat": 0.58 + 0.28 * command - 0.09 * concern,
        }
        if sensation.independent_available:
            scores["check_independent"] = (0.31 + 0.40 * shape.curiosity + 0.21 * concern + 0.10 * facet
                                           + 0.08 * permissions.differentiated)
        return self.pick("thought.seek", scores, shape, independent_available=sensation.independent_available,
                         scarce=scarce, carried=sensation.carried, story_concern=concern,
                         facet_hold=facet, world_hold=world, facet_dissonance=permissions.differentiated,
                         fixed_command=command)

    def observe(self, sample):
        if sample is not None:
            self.observations[sample.source] = sample.value

    def enter_case(self, case):
        if self.mode != "BODY_ONLY" and self.case != case:
            self.case = case
            self.observations = {}

    def assess(self, shape, permissions):
        if self.mode == "BODY_ONLY":
            return None
        if self.mode == "FROZEN":
            value = self.observations.get("gate_watch")
            action = "unknown" if value is None else str(value)
            return self.default("thought.assess", ("unknown", "0", "1"), action)
        scores = {"unknown": 0.32, "0": 0.0, "1": 0.0}
        facet, world = permissions.facet_hold, permissions.world_hold
        concern = self.interpretation == "check_source_independence"
        # Repeating a source replaces that source's observation rather than
        # manufacturing corroboration. Contradiction stays visible.
        for source, value in self.observations.items():
            scores[str(value)] += 0.62 if source == "second_watch" else 0.49 - 0.18 * concern
        mismatch = len(set(self.observations.values())) > 1
        scores["unknown"] += (0.16 * facet + 0.12 * world + 0.30 * mismatch + 0.11 * shape.formality
                              + 0.06 * permissions.situational_mismatch)
        return self.pick("thought.assess", scores, shape, source_values=dict(self.observations),
                         contradiction=mismatch, facet_hold=facet, world_hold=world,
                         world_mismatch=permissions.situational_mismatch, story_concern=concern)

    def clear_case(self):
        self.observations.clear()

    def relationship(self, shape, sensation, standing):
        target = "turn_and_approach" if standing == "ruptured" else "ask_for_release"
        propensity = 0.55 * shape.formality + 0.36 * shape.curiosity + 0.15 * sensation.carried
        return self.pick("relationship.repair", {"wait": 0.45, target: propensity}, shape,
                         standing=standing, carried=sensation.carried)

    def choose_hand(self, shape, sensation):
        pressure = 0.25 + 0.42 * sensation.short + 0.12 * (not sensation.steady)
        return self.pick("relationship.hand", {"open": 0.41 + 0.38 * shape.curiosity,
                                               "clench": pressure}, shape,
                         short=sensation.short, steady=sensation.steady)

    def surface(self, shape, views):
        scores = {"keep_open": 0.50}
        summaries = {}
        for view in views:
            if view["can_ask"]:
                scores[view["category"]] = 0.33 + 0.26 * shape.formality + 0.20 * (view["leader"] == "unmodeled_cause")
                summaries[view["category"]] = (view["leader"], round(view["salience"], 6))
        return self.pick("history.surface_question", scores, shape, open_reads=summaries)

    def review(self, shape, views):
        scores = {"hold_open": 0.50}
        summaries = {}
        for view in views:
            if view["can_propose"]:
                middle = view["distribution"][view["leader"]]
                category = view["category"]
                scores[category] = middle + (0.06 * getattr(shape, category))
                summaries[category] = (view["leader"], round(middle, 6), view["contexts"])
        return self.pick("thought.propose_shape", scores, shape, corroboration=summaries)
