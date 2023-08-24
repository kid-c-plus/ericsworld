import React from "react";
import Constants from "./constants.js";
import Wisp from "./Wisp.js";

// Root component for Wisp viewing screen
class WispScreen extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            wisps: []
        };
    }

    // Callback invoked after component mount
    componentDidMount() {
        this.loadWisps();
    }

    // Query backend for Wisps and update state object
    loadWisps(newestWispId=null, oldestWispId=null) {
        let params = new URLSearchParams()
        if (newestWispId) {
            params.append("newest_wisp_id", newestWispId);
        } else if (oldestWispId) {
            params.append("oldest_wisp_id", oldestWispId);
        }

        fetch(`${Constants.GET_WISPS_ENDPOINT}?${params}`)
        .then(response => response.json())
        .then(wisp_resp => {
            let wisps = wisp_resp["wisps"];
            if (newestWispId) {
                this.setState({
                    wisps: wisps.concat(this.state.wisps)
                });
            } else {
                this.setState({
                    wisps: this.state.wisps.concat(wisps)
                });
            }
        });
    }

    render() {
        let wispComponents = this.state.wisps.map(wisp => (
            <Wisp data={wisp} />
        ));
        return (
            <div id="WispScreen">
                {wispComponents}
            </div>
        );
    }
}

export default WispScreen;
