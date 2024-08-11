import React from "react";

// Component comprising functionality for custom scroll bar for Wisp 
// screen
class ScrollBar extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            scrollPercent: this.props.scrollPercent,
            scrollCallback: this.props.scrollCallback
        }

        this.domRef = React.createRef();
    }

    // click callback, jumps scroll to selected region
    handleClick(event) {
        let y = event.pageY;
        let rect = this.domRef.current.getBoundingClientRect();
        let percent = Math.max(
            0, Math.min((y - rect.top) / rect.height, 1)
        );
        this.props.scrollCallback(percent);
    }
        

    render() {
        return (
            <div id="ScrollBar" ref={this.domRef} 
                    onClick={this.handleClick.bind(this)} >
                <ScrollThumb scrollPercent={this.state.scrollPercent} 
                    dragHandler={this.handleClick.bind(this)} />
            </div>
        );
    }
}

// Component comprising scroll thumb, incl. image, for scroll bar
class ScrollThumb extends React.Component {
    constructor(props) { 
        super(props);

        this.state = {
            scrollPercent: props.scrollPercent,
            image: "apple.gif"
        }

        this.domRef = React.createRef();
    }
    
    // onMouseDown handler - registers onMouseMove/Up events for
    // entire document, so drag still works if cursor exits scrollbar
    // div
    handleMouseDown() {
        document.onmousemove = this.props.dragHandler;
        document.onmouseup = this.handleMouseUp.bind(this);
    }

    // document-wide onMouseUp handler set by above - deregisters
    // move and up events
    handleMouseUp() {
        document.onmousemove = null;
        document.onmouseup = null;
    }

    render() {
        return (
            <img id="ScrollThumb" draggable="false"
            alt={`scroll thumb - ${this.state.image}`}
            src={
                `assets/${this.state.image}`
            } ref={this.domRef} 
            onMouseDown={this.handleMouseDown.bind(this)} />
        );
    }
}

export default ScrollBar;
