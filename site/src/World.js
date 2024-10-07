import React from "react";

import WispScreen from "./WispScreen.js";
import ScrollBar from "./ScrollBar.js";
import Button from "./Button.js";
import AccountPane from "./AccountPane.js";
import WispPostPane from "./WispPostPane.js";

import Constants from "./constants.js";
import calculateViewportOffsets from "./onLoad.js";

import "./World.css";
import "./Pane.css";

// Root component for Eric's World app. Handles basic window sizing
// actions and polls backend
class World extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            csrfToken: "",

            thumbPercent: 0.0,

            selectedPane: "home",
            paneDeactivated: false,

            accountInfo: null,

            refreshCallback:    null
        }
        
        calculateViewportOffsets();
        document.body.onresize = calculateViewportOffsets;
    }

    // Callback invoked after component mount
    componentDidMount() {
        this.getCSRFToken();
        this.getAccountInfo();
    }

    // Gets CSRF token from "/hai" endpoint and saves to "csrfToken"
    // state element
    getCSRFToken() {
        fetch(Constants.CSRF_ENDPOINT, {
            credentials: "include"
        })
        .then(response => response.json())
        .then(csrfResp =>
            this.setState({
                csrfToken: csrfResp["csrftoken"]
            })
        );
    }

    // Backend Query Methods
    // Any backend data needed by multiple children
    // is done by the World component

    // helper method for fetch calls including CSRF token
    // also adds Content-Type: "application/json" header,
    // though that can be overridden by provided headers
    // endpoint - URL to query
    // params - query parameter dict to pass to fetch
    csrfFetch(endpoint, params) {
        let addedHeaders = {
            "X-CSRFToken": this.state.csrfToken,
            "Content-Type": "application/json"
        };
        params["headers"] = {
            ...addedHeaders,
            ...("headers" in params ? params["headers"] : {})
        }
        return fetch(endpoint, params);
    }

    // query backend for currently logged in account information
    // conditions on presence of "error" key in response, indicating
    // an unauthenticated user and 401 response. seems like a simpler
    // control flow than conditioning on status code
    getAccountInfo() {
        fetch(Constants.ACCOUNT_INFO_ENDPOINT, {
            credentials: "include"
        })
        .then(response => response.json())
        .then(accountInfoResp => {
            if ("error" in accountInfoResp) {
                this.setState({
                    accountInfo: null
                });
            } else {
                this.setState({
                    accountInfo: accountInfoResp
                });
            }
        })
    }
    
    // callback method for updating Wisp screen scroll percentage
    // newThumbPercent - scroll thumb percent, expressed as scrollTop / 
    //      (scrollHeight - clientHeight), thus has value 1 at bottom
    //      of scroll
    scrollCallback(newThumbPercent) {
        if (this.state.thumbPercent !== newThumbPercent) {
            this.setState({
                thumbPercent: newThumbPercent
            });
            document.documentElement.style.setProperty(
                "--scrollthumbpercent", newThumbPercent
            );
        }
    }

    // callback for registering WispScreen's own "refreshWisps"
    // callback as an element of the parent
    registerRefreshCallback(refreshCallback) {
        this.setState({
            refreshCallback: refreshCallback
        })
    }

    // callback for all pane selection Button children (i.e. About,
    // Account/Login, & Post). Sets state. should be bound with
    // appropriate state string. Can be bound with "home" to provide
    // panes themselves a graceful way of deactivating themselves
    paneButtonCallback(paneName) {
        if (paneName === this.state.selectedPane) {
            paneName = "home";
        }
        if (this.state.selectedPane === "home") {
            this.setState({selectedPane: paneName});
        } else {
            this.setState({paneDeactivated: true});
            setTimeout(() => this.setState({
                    selectedPane:       paneName,
                    paneDeactivated:    false
                }), 500
            );
        }
    }

    // renders selected pane inside of PaneContainer allowing for
    // pane closure on clicks outside pane window
    renderPane() {
        // prevents propogated clicks on children from closing
        // pane view
        let handleClick = (clickEvent) => {
            if (clickEvent.target.id === "PaneContainer") {
                this.paneButtonCallback("home");
            }
        }

        if (this.state.selectedPane === "home") {
            return <> < />;
        } else {
            return (
                <div id="PaneContainer" onClick={
                        handleClick}>
                    {this.renderSelectedPane()}
                </div>
            );
        }
    }

    // renderPane helper method, renders the currently selected pane
    renderSelectedPane() {
        switch (this.state.selectedPane) {
            case "account":
                return (
                    <AccountPane 
                        csrfFetch={this.csrfFetch.bind(this)}
                        accountInfo={
                            this.state.accountInfo}
                        accountUpdateCallback={
                            this.getAccountInfo.bind(this)}
                        profileEditorCallback={
                            this.paneButtonCallback.bind(
                                this, "profile")}
                        deactivateCallback={
                            this.paneButtonCallback.bind(
                                this, "home")}
                        deactivated={this.state.paneDeactivated}
                    />
                );
            case "post":
                return (
                    <WispPostPane
                        csrfFetch={this.csrfFetch.bind(this)}
                        refreshCallback={
                            this.state.refreshCallback}
                        deactivateCallback={
                            this.paneButtonCallback.bind(
                                this, "home")}
                        deactivated={this.state.paneDeactivated}
                    />
                );
            default:
                return <> < />;
        }
    }
 
    render() {
        return (
            <div id="World" className="ImageForeground">
                <Button elemId="HomeButton" pressCallback={
                    this.paneButtonCallback.bind(this, "home")} />
                <Button elemId="AboutButton" pressCallback={
                    this.paneButtonCallback.bind(this, "about")} />
                <Button elemId="AccountButton" pressCallback={
                    this.paneButtonCallback.bind(this, "account")} />
                <Button elemId="PostButton" pressCallback={
                    this.paneButtonCallback.bind(this, "post")} />

                <WispScreen thumbPercent={
                        this.state.thumbPercent
                    } scrollCallback={
                        this.scrollCallback.bind(this)
                    } 
                    registerRefreshCallback={
                        this.registerRefreshCallback.bind(
                            this)}
                />

                {this.renderPane()}

                <ScrollBar thumbPercent={
                        this.state.thumbPercent
                    } scrollCallback={
                        this.scrollCallback.bind(this)
                    }
               />
            </div>
        );
    }
}

export default World;
