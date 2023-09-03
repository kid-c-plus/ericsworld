import React from "react";
import PhoneInput from 'react-phone-input-2';
import "./PhoneInput.css";
import Constants from "./constants.js";

class AccountUpdatePane extends React.Component {
    constructor(props) {
        super(props);

        this.state = ({
            username:       this.props.accountInfo.username,
            profileUri:     this.props.accountInfo.profileUri,

            usernameUnique: true,
            
            errorMsg:   ""
        });
    }

    // Update an account element at the provided endpoint
    // by POSTing the provided body
    updateElement(endpoint, body, domEvent) {
        // on clicks and Enter keypress
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === 13) {
            this.props.csrfFetch(
                Constants.UPDATE_USERNAME_ENDPOINT,
                {
                    method:         "POST",
                    credentials:    "include",
                    body:           JSON.stringify(body)
                })
            .then(response => {
                if (response.status === 200) {
            }).then(errorResp => {
                if ("error" in errorResp) {
                    this.setState({errorMsg: errorResp["error"]});
                }
            }).catch(error => {
                console.log(`Error logging in: ${error.message}`);
            })
        }


    render() {
        return (
            <div id="AccountUpdatePane" className={
                    `Pane BoxShadow ${this.props.deactivated ?
                        "Deactivated" : ""
                     }`}>
                <div className="FormElement TextEntry WithSubmit">
                    <span className="EntryLabel">User Name:</span>
                    <input type="text" id="UsernameInput"
                        name="UsernameInput" className="TextInput"
                        maxLength={`${Constants.USERNAME_LENGTH}`}
                        value={this.state.username}
                        onChange={changeEvent => {
                            this.setState({
                                username: changeEvent.target.value
                            })}}
                        onKeyUp={this.updateElement.bind(
                            this, Constants.UPDATE_USERNAME_ELEMENT,
                            {"username": this.state.username})}
                    />
                </div>
            </div>
        );
    }
}

export default AccountUpdatePane;
