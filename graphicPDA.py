
from manim import *

from textBasedPDA import PushDownAutomaton


class PushDownAutomatonViewer(Scene):
    def construct(self):
        pda = PushDownAutomaton("TestPDA.txt")
        # draw state diagram?
        pda.determinePath("0011")
        self.initialScreen(pda)
        while pda.is_processing:
            pda.transition()
            # self.updateScreen(pda)

    def initialScreen(self, pda):
        group = VGroup()
        for symbol in pda.input_str:
            sym = Text(symbol, color=BLUE, stroke_width=0)
            group.add(sym)
        group.arrange(RIGHT, buff=.5)
        self.play(Write(group))
        self.wait(1)
