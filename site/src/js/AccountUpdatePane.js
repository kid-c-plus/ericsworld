import React from "react";
import PhoneInput from 'react-phone-input-2';

import Constants from "./constants.js";
import UsernameUpdateSubpane from "./UsernameUpdateSubpane.js";
import ProfileUpdateSubpane from "./ProfileUpdateSubpane.js";

// React component for changing account items (i.e. username, profile)
class AccountUpdatePane extends React.Component {
    constructor(props) {
        super(props);

        this.state = ({
            // the element currently being changed
            selectedSubpane:    "profile pic",

            // whether the server sent out an auth code
            enteringAuthCode:   false,

            // any error message returned by the server
            errorMsg:   null
        });
    }

    // Update an account element at the provided endpoint
    // by POSTing the provided body
    updateElement(endpoint, body, domEvent) {
        // on clicks and Enter keypress
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === 13) {
            this.props.csrfFetch(
                endpoint,
                {
                    method:         "POST",
                    credentials:    "include",
                    body:           JSON.stringify(body)
                }
            ).then(response => {
                if (response.status === 200) {
                    this.stopChangeCallback();
                    this.props.updateCallback();
                } else if (response.statusCode === 204) {
                    this.setState({enteringAuthCode: true});
                }
                return response.json();
            }).then(errorResp => {
                if ("error" in errorResp) {
                    this.setState({errorMsg: errorResp["error"]});
                }
            }).catch(error => {
                console.log(`Error updating account: ${error.message}`);
            })
        }
    }

    // Logs out current user
    logout() {
        this.props.csrfFetch(
            Constants.LOGOUT_ENDPOINT,
            {
                method:         "POST",
                credentials:    "include"
            }
        ).then(response => {
            if (response.status === 200) {
                this.props.updateCallback();
                this.props.deactivateCallback();
            }
        });
    }

    // simple callback to leave element change window
    stopChangeCallback() {
        this.setState({
            selectedSubpane:    null,
            enteringAuthCode:   false,
            errorMsg:           null
        })
    }

    renderSelectedSubpane() {
        switch (this.state.selectedSubpane) {
            case "username":
                return (
                    <UsernameUpdateSubpane username={
                            this.props.accountInfo.username}
                        updateUsername={
                            this.updateElement.bind(
                            this, Constants.UPDATE_USERNAME_ENDPOINT)}
                        cancel={() =>
                            this.setState({
                                selectedSubpane: null
                            })}
                    /> 
                );
            case "profile pic":
                return (
                    <ProfileUpdateSubpane
                        updateProfile={
                            this.updateElement.bind(
                            this, Constants.UPDATE_PROFILE_ENDPOINT)}
                        cancel={() =>
                            this.setState({
                                selectedSubpane: null
                            })}
                    />
                );
            default:
                let buttons = ["username", "profile pic", 
                    "phone number", "password", 
                    "recovery email"].map(element => (
                        <div className="FormElement Half" 
                                key={`${element}UpdateButton`}>
                            <div className="FormButton Fit BoxShadow" 
                                    onClick={() => this.setState({
                                        selectedSubpane: element
                                    })}>
                                {`update ${element}`}
                            </div>
                        </div>
                    ));
                return (
                    <div id="UpdateOptionsSubpane" className="Subpane">
                        {buttons}
                        <div className="FormElement Half">
                            <div className="FormButton Fit BoxShadow"
                                    onClick={this.logout.bind(this)}>
                                logout
                            </div>
                        </div>
                    </div>
                );

        }
    }

    render() {
        return (
            <div id="AccountUpdatePane" className={
                    `Pane BoxShadow ${this.props.deactivated ?
                        "Deactivated" : ""
                     }`}>
                 {this.renderSelectedSubpane()}
            </div>
        );
    }
}

export default AccountUpdatePane;
