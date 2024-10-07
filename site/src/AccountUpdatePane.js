import React from "react";
import PhoneInput from 'react-phone-input-2';
import "./PhoneInput.css";
import Constants from "./constants.js";

// React component for changing account items (i.e. username, profile)
class AccountUpdatePane extends React.Component {
    constructor(props) {
        super(props);

        this.state = ({
            // the element currently being changed
            selectedSubpane:    null,

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

class UsernameUpdateSubpane extends React.Component {
    constructor(props) {
        super(props);
        console.log(this.props);

        this.state = {
            username:   this.props.username,
            unique:     true
        }
    }

    // query API to check if provided username is standard
    checkUniqueness(username) {
        if (username.length >= Constants.MIN_USERNAME_LENGTH && 
                username.length <= Constants.MAX_USERNAME_LENGTH) {
            let searchParams = new URLSearchParams({
                username: username
            })
            fetch(
                Constants.CHECK_USERNAME_ENDPOINT + "?" + searchParams,
                {
                    method: "GET"
                }
            ).then(response => response.json())
            .then(uniqueResp => {
                this.setState({unique: uniqueResp["unique"]})
            });
        }
    }

    // keyup and click handler for username update field
    // submits on button click and enter keypress
    submit(domEvent) {
        if ((domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === 13) && this.state.unique) {
            this.props.updateUsername(
                {"new_username": this.state.username}, null
            );
        } 
    }

    // change handler for username field. computes uniqueness
    usernameChanged(changeEvent) {
        this.setState({
            username: changeEvent.target.value});
        this.checkUniqueness(changeEvent.target.value);
    }

    render() {
        let uniqueStatus = "";
        if (this.state.username && this.state.username.length >= 
                Constants.MIN_USERNAME_LENGTH) {
            if (this.state.username === this.props.username) {
                uniqueStatus = "this one's your name"
            } else if (this.state.unique) {
                uniqueStatus = "this one's available";
            } else {
                uniqueStatus = "this one's unavailable";
            }
        } else {
            uniqueStatus = "enter a new username";
        }
        
        return (
            <div id="UpdateUsernameSubpane" className="Subpane">
                <div className="FormElement TextEntry">
                    <span className="EntryLabel">User Name:</span>
                    <input type="text" id="UsernameInput"
                        name="UsernameInput" className="TextInput"
                        maxLength={`${Constants.MAX_USERNAME_LENGTH}`}
                        value={this.state.username}
                        onChange={this.usernameChanged.bind(this)}
                        onKeyUp={this.submit.bind(this)}
                    />
                </div>
                <div className="FormElement Status">
                    {uniqueStatus}
                </div>
                <div className="FormElement">
                    <div className="FormButton BoxShadow"
                        onClick={this.submit.bind(this)}>
                        update
                    </div>
                </div>
            </div>
        );
    }
}

export default AccountUpdatePane;
