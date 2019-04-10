# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Input(Component):
    """A Input component.


Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- style (dict; optional): Defines CSS styles which will override styles previously set.
- className (string; optional): Often used with CSS to style elements with common properties.
- key (string; optional): A unique identifier for the component, used to improve
performance by React.js while rendering components
See https://reactjs.org/docs/lists-and-keys.html for more info
- type (a value equal to: "text", 'number', 'password', 'email', 'range', 'search', 'tel', 'url', 'hidden'; optional): The type of control to render
- value (string; optional): The value of the Input
- disabled (boolean; optional): If true, the input is disabled and can't be clicked on.
- size (string; optional): The initial size of the control. This value is in pixels unless the value
of the type attribute is text or password, in which case it is an integer
number of characters. This attribute applies only when the type attribute
is set to text, search, tel, url, email, or password, otherwise it is
ignored. In addition, the size must be greater than zero. If you do not
specify a size, a default value of 20 is used.
- bs_size (string; optional): Set the size of the Input. Options: 'sm' (small), 'md' (medium)
or 'lg' (large). Default is 'md'.
- valid (boolean; optional): Apply valid style to the Input for feedback purposes. This will cause
any FormFeedback in the enclosing FormGroup with valid=True to display.
- invalid (boolean; optional): Apply invalid style to the Input for feedback purposes. This will cause
any FormFeedback in the enclosing FormGroup with valid=False to display.
- plaintext (boolean; optional): Set to true for a readonly input styled as plain text with the default
form field styling removed and the correct margins and padding preserved.
- placeholder (string; optional): A hint to the user of what can be entered in the control . The placeholder
text must not contain carriage returns or line-feeds. Note: Do not use the
placeholder attribute instead of a <label> element, their purposes are
different. The <label> attribute describes the role of the form element
(i.e. it indicates what kind of information is expected), and the
placeholder attribute is a hint about the format that the content should
take. There are cases in which the placeholder attribute is never
displayed to the user, so the form must be understandable without it.
- name (string; optional): The name of the control, which is submitted with the form data.
- n_submit (number; optional): Number of times the `Enter` key was pressed while the input had focus.
- n_submit_timestamp (number; optional): Last time that `Enter` was pressed.
- n_blur (number; optional): Number of times the input lost focus.
- n_blur_timestamp (number; optional): Last time the input lost focus.
- debounce (boolean; optional): If true, changes to input will be sent back to the Dash server
only when the enter key is pressed or when the component loses
focus.  If it's false, it will sent the value back on every
change.
- loading_state (optional): Object that holds the loading state object coming from dash-renderer. loading_state has the following type: dict containing keys 'is_loading', 'prop_name', 'component_name'.
Those keys have the following types:
  - is_loading (boolean; optional): Determines if the component is loading or not
  - prop_name (string; optional): Holds which property is loading
  - component_name (string; optional): Holds the name of the component that is loading"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, style=Component.UNDEFINED, className=Component.UNDEFINED, key=Component.UNDEFINED, type=Component.UNDEFINED, value=Component.UNDEFINED, disabled=Component.UNDEFINED, size=Component.UNDEFINED, bs_size=Component.UNDEFINED, valid=Component.UNDEFINED, invalid=Component.UNDEFINED, plaintext=Component.UNDEFINED, placeholder=Component.UNDEFINED, name=Component.UNDEFINED, n_submit=Component.UNDEFINED, n_submit_timestamp=Component.UNDEFINED, n_blur=Component.UNDEFINED, n_blur_timestamp=Component.UNDEFINED, debounce=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'style', 'className', 'key', 'type', 'value', 'disabled', 'size', 'bs_size', 'valid', 'invalid', 'plaintext', 'placeholder', 'name', 'n_submit', 'n_submit_timestamp', 'n_blur', 'n_blur_timestamp', 'debounce', 'loading_state']
        self._type = 'Input'
        self._namespace = 'dash_bootstrap_components/_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'style', 'className', 'key', 'type', 'value', 'disabled', 'size', 'bs_size', 'valid', 'invalid', 'plaintext', 'placeholder', 'name', 'n_submit', 'n_submit_timestamp', 'n_blur', 'n_blur_timestamp', 'debounce', 'loading_state']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Input, self).__init__(**args)
