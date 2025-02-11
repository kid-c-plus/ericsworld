import React from "react";

import Constants from "./constants.js";
import Wisp from "./Wisp.js";

// Root component for Wisp viewing screen
class WispScreen extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            wisps: [],
        };

        this.domRef = React.createRef();

        // pass "getWisps" back to the parent
        this.props.registerRefreshCallback(this.getWisps.bind(this));

        // set to true immediately after manually updating scrollTop,
        // as opposed to recieving user scroll. Both actions invoke
        // the onScroll callback, but only user scroll should invoke
        // the parent's scrollCallback function
        this.scrollTopUpdated = false;

        // ratio of Thumb Scroll percent (goes from 0 to 1) to
        // actual screen top scroll percent (goes from 0 to 
        // (scrollHeight - clientHeight) / scrollHeight)
        this.scrollRatio = 1.0;
    }

    componentDidMount() {
        this.getWisps();
        // The scrollbar has an unfortunate tendency to get
        // stuck, so this should run periodically to make sure the 
        // CSS variable is kept current
        setInterval(this.updateScroll.bind(this), 250);
    }

    // Query backend for Wisps and update state object
    getWisps(newestWispId=null, oldestWispId=null) {
        console.log("getting wisps...");
        let params = new URLSearchParams();
        if (newestWispId === null && oldestWispId === null &&
                this.state.wisps.length > 0) {
            newestWispId = this.state.wisps[0]["wisp_id"];
        }
        if (newestWispId) {
            params.append("newest_wisp_id", newestWispId);
        } else if (oldestWispId) {
            params.append("oldest_wisp_id", oldestWispId);
        }

        fetch(`${Constants.GET_WISPS_ENDPOINT}?${params}`)
        .then(response => response.json())
        .then(wispResp => {
            let wisps = wispResp["wisps"];
            console.log(wisps);
            if (newestWispId) {
                this.setState({
                    wisps: wisps.concat(this.state.wisps)
                });
            } else if (oldestWispId) {
                this.setState({
                    wisps: this.state.wisps.concat(wisps)
                });
            } else {
                wisps = wisps.filter(wisp => {
                    for (var existing_wisp in this.state.wisps) {
                        if (wisp["wisp_id"] === 
                                existing_wisp["wisp_id"]) {
                            return false;
                        }
                    }
                    return true;
                });
                this.setState({
                    wisps: wisps.concat(this.state.wisps)
                });
            }
            // update scroll value
            this.updateScroll();
        });
    }

    // handler for onScroll DOM event. calculates scroll percent
    // and calls parent's scrollCallback
    updateScroll() {
        // programattically changing the value of scrollTop
        // causes this method to be called, but no action should
        // be taken unless user manually scrolls
        if (this.scrollTopUpdated) {
            this.scrollTopUpdated = false;
        } else {
            if (this.domRef.current) {
                let elem = this.domRef.current;
                if (elem.scrollHeight > elem.clientHeight) {
                    this.scrollRatio = (
                        (elem.scrollHeight - elem.clientHeight) /
                        elem.scrollHeight
                    );
                    let scrollThumbPercent = (
                        elem.scrollTop / (
                            elem.scrollHeight - elem.clientHeight
                        )
                    );
                    this.props.scrollCallback(
                        scrollThumbPercent
                    );
                }
            }
        }
    }

    componentDidUpdate() {
        this.updateScroll();
    }

    render() {
        let wispComponents = this.state.wisps.map(wisp => (
            <Wisp data={wisp} key={wisp["wisp_id"]} />
        ));
        console.log(this.state.wisps);
        if (this.domRef.current) {
            this.scrollTopUpdated = true;
            this.domRef.current.scrollTop = (
                this.domRef.current.scrollHeight * 
                this.props.thumbPercent *
                this.scrollRatio
            );
        }
        return (
            <div id="WispScreen" className="ImageForeground"
                    ref={this.domRef} 
                    onScroll={this.updateScroll.bind(this)} >
                {wispComponents}
            </div>
        );
    }
}

export default WispScreen;
