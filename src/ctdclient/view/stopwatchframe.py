import datetime

import customtkinter as ctk
from ctdclient.view.ctkframe import CtkFrame


class StopwatchFrame(CtkFrame):
    """Frame that acts as a simple stopwatch."""

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.color = "gray14"

        self.timer_seconds = 0
        self.stopwatch_label = ctk.CTkLabel(
            self,
            height=70,
            width=70,
            corner_radius=200,
            text="00:00:00",
            font=("Normal", 15, "bold"),
        )
        self.stopwatch_label.configure(fg_color=self.color)
        self.stopwatch_label.grid()

        self.stopwatch_label.bind("<Button-1>", self.reset)
        self.stopwatch_label.bind(
            "<Enter>",
            command=lambda e: self.stopwatch_label.configure(
                fg_color="#1f538d"
            ),
        )
        self.stopwatch_label.bind(
            "<Leave>",
            command=lambda e: self.stopwatch_label.configure(
                fg_color=self.color
            ),
        )
        self.update()

    def update(self):
        self.timer_seconds += 1
        self.stopwatch_label.configure(
            text=str(datetime.timedelta(seconds=self.timer_seconds))
        )
        self.stopwatch_label.after(1000, self.update)

    def reset(self, event):
        self.timer_seconds = 0
