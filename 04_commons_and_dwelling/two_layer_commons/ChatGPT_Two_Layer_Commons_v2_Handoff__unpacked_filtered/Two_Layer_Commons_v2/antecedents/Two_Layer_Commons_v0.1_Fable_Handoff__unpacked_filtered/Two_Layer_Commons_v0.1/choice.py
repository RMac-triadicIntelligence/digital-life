"""Member policy and finite choice history; no imports from the body or kernel."""
from collections import deque


class Choice:
    CAPACITY = 72

    def __init__(self, mode, clench_enabled):
        self.mode = mode
        self.clench_enabled = clench_enabled
        self.history = deque(maxlen=self.CAPACITY)
        self.paid_attention = False
        self.approached = False

    def select(self, topic, options, selection):
        row = {"topic": topic, "options": list(options), "selected": selection}
        if self.mode == "ACTIVE":
            self.history.append(row)
        return row

    def request(self, first_opportunity, story_marker):
        if self.mode != "ACTIVE" or not first_opportunity:
            return None
        action = "ask" if story_marker else "pass"
        return self.select("history", ("ask", "pass"), action)

    def receive_story(self, story):
        self.paid_attention = story == "two observations can come from one source"

    def decide(self, tick, feeling, incident):
        if self.mode == "BODY_ONLY":
            return ()
        options = ("wait", "check_repeat", "check_independent") if feeling.independent_available else ("wait", "check_repeat")
        if self.mode == "FROZEN":
            return (self.select("thought", options, "check_repeat"),)
        action = "wait"
        if feeling.short:
            action = "wait"
        elif feeling.independent_available and (self.paid_attention or not feeling.settled or tick % 3 == 1):
            action = "check_independent"
        elif feeling.settled:
            action = "check_repeat"
        choices = [self.select("thought", options, action)]
        if incident == "observed" and feeling.needs_repair and not self.approached:
            choices.append(self.select("relationship", ("turn_and_approach", "leave"), "turn_and_approach"))
            self.approached = True
        elif incident == "approached" and feeling.needs_repair:
            choices.append(self.select("relationship", ("ask_for_release", "leave"), "ask_for_release"))
        if self.clench_enabled:
            hand = "clench" if feeling.short or tick % 3 == 0 else "open"
            choices.append(self.select("relationship_hand", ("open", "clench"), hand))
        if tick == 9:
            choices.append(self.select("thought_protected_proposal", ("propose", "defer"),
                                       "propose" if feeling.settled else "defer"))
        return choices

    def assess(self, evidence):
        if self.mode == "BODY_ONLY" or evidence is None:
            return None
        options = ("hold", "zero", "one")
        decision = ("zero", "one")[evidence["reading"]]
        if self.mode == "ACTIVE" and self.paid_attention and evidence["source"] == "repeat":
            decision = "hold"
        return self.select("thought_assessment", options, decision)
