"""
A toggle button widget.
"""
from collections.abc import Callable

from wcwidth import wcswidth

from .behaviors.themable import Themable
from .behaviors.toggle_button_behavior import (
    ButtonState,
    ToggleButtonBehavior,
    ToggleState,
)
from .text_widget import TextWidget
from .widget import Widget

CHECK_OFF = "□ "
CHECK_ON = "▣ "
TOGGLE_OFF = "◯ "
TOGGLE_ON = "◉ "


class ToggleButton(Themable, ToggleButtonBehavior, Widget):
    """
    A toggle button widget. Without a group, a toggle button acts like a checkbox.
    With a group it behaves like a radio button (only a single button in a group is
    allowed to be in the "on" state).

    Parameters
    ----------
    label : str, default: ""
        Toggle button label.
    callback : Callable[[ToggleState], None], default: lambda: None
        Called when toggle state changes. The new state is provided as first argument.
    group : None | Hashable, default: None
        If a group is provided, only one button in a group can be in the "on" state.
    allow_no_selection : bool, default: False
        If a group is provided, setting this to true allows no selection, i.e.,
        every button can be in the "off" state.
    toggle_state : ToggleState, default: ToggleState.OFF
        Initial toggle state of button. If button is in a group and
        :attr:`allow_no_selection` is false this value will be ignored if all buttons
        would be "off".
    always_release : bool, default: False
        Whether a mouse up event outside the button will trigger it.
    size : Size, default: Size(10, 10)
        Size of widget.
    pos : Point, default: Point(0, 0)
        Position of upper-left corner in parent.
    size_hint : SizeHint, default: SizeHint(None, None)
        Proportion of parent's height and width. Non-None values will have
        precedent over :attr:`size`.
    min_height : int | None, default: None
        Minimum height set due to size_hint. Ignored if corresponding size
        hint is None.
    max_height : int | None, default: None
        Maximum height set due to size_hint. Ignored if corresponding size
        hint is None.
    min_width : int | None, default: None
        Minimum width set due to size_hint. Ignored if corresponding size
        hint is None.
    max_width : int | None, default: None
        Maximum width set due to size_hint. Ignored if corresponding size
        hint is None.
    pos_hint : PosHint, default: PosHint(None, None)
        Position as a proportion of parent's height and width. Non-None values
        will have precedent over :attr:`pos`.
    anchor : Anchor, default: "center"
        The point of the widget attached to :attr:`pos_hint`.
    is_transparent : bool, default: False
        If true, background_char and background_color_pair won't be painted.
    is_visible : bool, default: True
        If false, widget won't be painted, but still dispatched.
    is_enabled : bool, default: True
        If false, widget won't be painted or dispatched.
    background_char : str | None, default: None
        The background character of the widget if not `None` and if the widget
        is not transparent.
    background_color_pair : ColorPair | None, default: None
        The background color pair of the widget if not `None` and if the
        widget is not transparent.

    Attributes
    ----------
    label : str
        Toggle button label.
    callback : Callable[[ToggleState], None]
        Button callback when toggled.
    group : None | Hashable
        If a group is provided, only one button in a group can be in the "on" state.
    allow_no_selection : bool
        If true and button is in a group, every button can be in the "off" state.
    toggle_state : ToggleState
        Toggle state of button.
    always_release : bool
        Whether a mouse up event outside the button will trigger it.
    state : ButtonState
        Current button state. One of `NORMAL`, `HOVER`, `DOWN`.
    size : Size
        Size of widget.
    height : int
        Height of widget.
    rows : int
        Alias for :attr:`height`.
    width : int
        Width of widget.
    columns : int
        Alias for :attr:`width`.
    pos : Point
        Position relative to parent.
    top : int
        Y-coordinate of position.
    y : int
        Y-coordinate of position.
    left : int
        X-coordinate of position.
    x : int
        X-coordinate of position.
    bottom : int
        :attr:`top` + :attr:`height`.
    right : int
        :attr:`left` + :attr:`width`.
    absolute_pos : Point
        Absolute position on screen.
    center : Point
        Center of widget in local coordinates.
    size_hint : SizeHint
        Size as a proportion of parent's size.
    height_hint : float | None
        Height as a proportion of parent's height.
    width_hint : float | None
        Width as a proportion of parent's width.
    min_height : int
        Minimum height allowed when using :attr:`size_hint`.
    max_height : int
        Maximum height allowed when using :attr:`size_hint`.
    min_width : int
        Minimum width allowed when using :attr:`size_hint`.
    max_width : int
        Maximum width allowed when using :attr:`size_hint`.
    pos_hint : PosHint
        Position as a proportion of parent's size.
    y_hint : float | None
        Vertical position as a proportion of parent's size.
    x_hint : float | None
        Horizontal position as a proportion of parent's size.
    anchor : Anchor
        Determines which point is attached to :attr:`pos_hint`.
    background_char : str | None
        Background character.
    background_color_pair : ColorPair | None
        Background color pair.
    parent : Widget | None
        Parent widget.
    children : list[Widget]
        Children widgets.
    is_transparent : bool
        True if widget is transparent.
    is_visible : bool
        True if widget is visible.
    is_enabled : bool
        True if widget is enabled.
    root : Widget | None
        If widget is in widget tree, return the root widget.
    app : App
        The running app.

    Methods
    -------
    update_theme:
        Paint the widget with current theme.
    update_off:
        Paint the "off" state.
    update_on:
        Paint the "on" state.
    on_toggle:
        Called when the toggle state changes.
    update_normal:
        Paint the normal state.
    update_hover:
        Paint the hover state.
    update_down:
        Paint the down state.
    on_release:
        Triggered when a button is released.
    on_size:
        Called when widget is resized.
    apply_hints:
        Apply size and pos hints.
    to_local:
        Convert point in absolute coordinates to local coordinates.
    collides_point:
        True if point is within widget's bounding box.
    collides_widget:
        True if other is within widget's bounding box.
    add_widget:
        Add a child widget.
    add_widgets:
        Add multiple child widgets.
    remove_widget:
        Remove a child widget.
    pull_to_front:
        Move to end of widget stack so widget is drawn last.
    walk_from_root:
        Yield all descendents of root widget.
    walk:
        Yield all descendents (or ancestors if `reverse` is true).
    subscribe:
        Subscribe to a widget property.
    unsubscribe:
        Unsubscribe to a widget property.
    on_key:
        Handle key press event.
    on_mouse:
        Handle mouse event.
    on_paste:
        Handle paste event.
    tween:
        Sequentially update a widget property over time.
    on_add:
        Called after a widget is added to widget tree.
    on_remove:
        Called before widget is removed from widget tree.
    prolicide:
        Recursively remove all children.
    destroy:
        Destroy this widget and all descendents.
    """

    def __init__(
        self,
        *,
        background_char=" ",
        label: str = "",
        callback: Callable[[ToggleState], None] = lambda state: None,
        **kwargs,
    ):
        self.normal_color_pair = (0,) * 6  # Temporary assignment

        self._label_widget = TextWidget(pos_hint=(0.5, 0), anchor="left")

        self.callback = callback  # This must be set before `super().__init__`.

        super().__init__(background_char=background_char, **kwargs)

        self.add_widget(self._label_widget)

        self.label = label

    def update_theme(self):
        match self.state:
            case ButtonState.NORMAL:
                self.update_normal()
            case ButtonState.HOVER:
                self.update_hover()
            case ButtonState.DOWN:
                self.update_down()

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str):
        self._label = label

        if self.group is None:
            if self.toggle_state is ToggleState.OFF:
                prefix = CHECK_OFF
            else:
                prefix = CHECK_ON
        else:
            if self.toggle_state is ToggleState.OFF:
                prefix = TOGGLE_OFF
            else:
                prefix = TOGGLE_ON

        text = prefix + label
        self._label_widget.size = 1, wcswidth(text)
        self._label_widget.apply_hints()
        self._label_widget.add_str(text)

    def update_hover(self):
        self.background_color_pair = self._label_widget.colors[
            :
        ] = self.color_theme.button_hover

    def update_down(self):
        self.background_color_pair = self._label_widget.colors[
            :
        ] = self.color_theme.button_press

    def update_normal(self):
        self.background_color_pair = self._label_widget.colors[
            :
        ] = self.color_theme.button_normal

    def on_toggle(self):
        if (
            self._label_widget.parent is not None
        ):  # This will be false during initialization.
            self.label = self.label  # Update radio button/checkbox
        self.callback(self.toggle_state)
