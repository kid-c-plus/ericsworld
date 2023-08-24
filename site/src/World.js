import React from "react";
import WispScreen from "./WispScreen.js";
import Constants from "./constants.js";
import calculateViewportOffsets from "./onLoad.js";
import "./World.css";

// Root component for Eric's World app. Handles basic window sizing
// actions and polls backend
class World extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            csrfToken: ""
        }
        
        calculateViewportOffsets();
        document.body.onresize = calculateViewportOffsets;
    }

    // Callback invoked after component mount
    componentDidMount() {
        this.getCSRFToken();
        console.log(document.cookie);
    }

    // Gets CSRF token from "/hai" endpoint and saves to "csrfToken"
    // state element
    getCSRFToken() {
        fetch(Constants.CSRF_ENDPOINT, {
            credentials: "include"
        })
        .then(response => response.text())
        .then(text =>
            this.setState({
                csrfToken: text
            })
        );
    }

    // helper method for fetch calls including CSRF token
    // endpoint - URL to query
    // params - query parameter dict to pass to fetch
    csrfFetch(endpoint, params) {
        if ("headers" in params) {
            params["headers"]["X-CSRFToken"] = this.state.csrfToken;
        } else {
            params["headers"] = {
                "X-CSRFToken": this.state.csrfToken
            };
        }
        return fetch(endpoint, params);
    }
  
    render() {
        return (
            <div id="World">
                <WispScreen />
            </div>
        );
    }
}

export default World;
