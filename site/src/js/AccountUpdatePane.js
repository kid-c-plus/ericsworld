import React from "react";

import Constants from "./constants.js";
import UsernameUpdateSubpane from "./UsernameUpdateSubpane.js";
import ProfileUpdateSubpane from "./ProfileUpdateSubpane.js";
import PhoneNumberUpdateSubpane from "./PhoneNumberUpdateSubpane.js";
import PasswordUpdateSubpane from "./PasswordUpdateSubpane.js";
import RecoveryEmailUpdateSubpane from 
    "./RecoveryEmailUpdateSubpane.js";

// React component for changing account items (i.e. username, profile)
class AccountUpdatePane extends React.Component {
    constructor(props) {
        super(props);

        this.state = ({
            // the element currently being changed
            selectedSubpane:    null,

            // whether the server sent out an auth code
            enteringAuthCode:   false,

            // any response message returned by the server
            responseMsg:    null,

            // any error message returned by the server
            errorMsg:   null,

            // both the above will be displayed as notifications
            // this allows
            notificationDeactivated: false
        });
    }

    // Update an account element at the provided endpoint
    // by POSTing the provided body
    updateElement(endpoint, body, domEvent) {
        // on clicks and Enter keypress
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === 13) {
            this.setState({responseMsg: "loading..."});
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
                } else if (response.status === 202) {
                    this.setState({enteringAuthCode: true});
                }
                return response.json();
            }).then(response => {
                // display messages in Notification pane, then
                // set to Deactivate and then disappear
                if ("error" in response) {
                    this.setState({errorMsg: response["error"]});
                } else if ("response" in response) {
                    this.setState({
                        responseMsg: response["response"]
                    })
                }
                setTimeout(() => this.setState({
                        notificationDeactivated: true
                    }), Constants.NOTIFICATION_DURATION);
                setTimeout(() => this.setState({
                        errorMsg:           null,
                        responseMsg:        null,
                        notificationDeactivated:    false
                    }), Constants.NOTIFICATION_DURATION +
                    Constants.DEACTIVATION_DURATION
                );
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
                                selectedSubpane: null,
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
            case "phone number":
                return (
                    <PhoneNumberUpdateSubpane
                        updatePhoneNumber={
                            this.updateElement.bind(this, 
                            Constants.UPDATE_PHONE_NUMBER_ENDPOINT)}
                        csrfFetch={this.state.csrfFetch}
                        enteringAuthCode={
                            this.state.enteringAuthCode}
                        cancel={() =>
                            this.setState({
                                selectedSubpane: null,
                                enteringAuthCode: false
                            })}
                    />
                );
            case "password":
                return (
                    <PasswordUpdateSubpane
                        updatePassword={
                            this.updateElement.bind(this,
                            Constants.UPDATE_PASSWORD_ENDPOINT
                            )}
                        cancel={() => 
                            this.setState({
                                selectedSubpane: null
                            })}
                     />
                );
            case "recovery email":
                return (
                    <RecoveryEmailUpdateSubpane
                        updateRecoveryEmail={
                            this.updateElement.bind(this,
                            Constants.UPDATE_RECOVERY_EMAIL_ENDPOINT
                            )}
                        recoveryEmail={
                            this.props.accountInfo.recovery_email}
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
                 {((this.state.responseMsg !== null && 
                    this.state.selectedSubpane == null)||
                    this.state.errorMsg !== null) ? 
                    <div className={
                        `Notification ${
                            this.state.notificationDeactivated ?
                            "Deactivated" : ""
                        }`}>
                        {
                            this.state.errorMsg !== null ?
                            this.state.errorMsg :
                            this.state.responseMsg
                        }
                    </div> : <> < /> }
            </div>
        );
    }
}

export default AccountUpdatePane;
