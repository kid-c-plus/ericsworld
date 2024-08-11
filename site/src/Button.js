import React from "react";

// Generic component for UI button overlay, including button press
// image display
class Button extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            pressed:    false
        };
    }

    // onMouseDown handler, functions as ScrollThumb does, registers
    // onMouseUp event for entire document, calls parent-provided
    // button press callback, and sets pressed state
    handleMouseDown() {
        this.setState({pressed: true});
        this.props.pressCallback();
        document.onmouseup = this.handleMouseUp.bind(this);
    }

    // document-wide onMouseUp handler - deregisters self and resets
    // pressed state
    handleMouseUp() {
        this.setState({pressed: false});
        document.onmouseup = null;
    }

    render() {
        return (
            <div id={this.props.elemId} className="PaneButton" 
            onMouseDown={this.handleMouseDown.bind(this)} >
                {this.state.pressed ? (
                    <img className="ButtonPressImg" src={
                        `assets/${this.props.elemId}_pressed.png`
                    } alt={`pressed ${this.props.elemId}`} />
                ) : <></>}
            </div>
        );
    }
}

export default Button
