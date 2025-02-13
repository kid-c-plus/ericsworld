import React from "react";
import PhoneInput from 'react-phone-input-2';

import Constants from "./constants.js";

// React component for "login" pane
class LoginPane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            phoneNumber:    "",
            password:       "",
            authCode:       "",
            remember:       false,

            enteringAuthCode:   false,

            errorMsg:   "", 

            // true while enter is pressed, for rendering button
            enterPressed:   false,
            // likewise with escape, for cancel button
            escapePressed:  false
        };

        this.authCodeRef = React.createRef();
    }

    login(authCode, domEvent) {
        // on clicks and Enter keypress
        this.setState({
            enterPressed:   false,
            escapePressed:  false
        });
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === 13) {
            let body = {
                phone_number:   `+${this.state.phoneNumber}`,
                password:       this.state.password,
                remember:       this.state.remember
            }
            if (this.state.enteringAuthCode) {
                if (authCode !== null) {
                    body["auth_code"] = authCode;
                } else {
                    body["auth_code"] = this.state.authCode;
                }
            }
            this.props.csrfFetch(
                Constants.LOGIN_ENDPOINT,
                {
                    method:         "POST",
                    credentials:    "include",
                    body:           JSON.stringify(body)
                })
            .then(response => {
                if (response.status === 200) {
                    this.props.deactivateCallback();
                    // prevent the account update pane from showing
                    // while the login pane is deactivating
                    setTimeout(
                        () => this.props.updateCallback(),
                        500
                    );
                } else if (response.status === 202) {
                    this.setState({enteringAuthCode: true});
                }
                return response.json()
            }).then(errorResp => {
                if ("error" in errorResp) {
                    this.setState({
                        errorMsg:   errorResp["error"],
                        authCode:   ""
                    });
                }
                setTimeout(
                    () => this.setState({
                        errorMsg: null
                    }), 1000
                );
                console.log(errorResp);
            }).catch(error => {
                console.log(`Error logging in: ${error.message}`);
            })
        } else if (domEvent.keyCode === Constants.ESCAPE_KEY) {
            this.setState({
                authCode: "",
                enteringAuthCode: false
            });
        }
    }

    // onChange callback for auth code entry fields - 
    // ensures only numbers are entered, maintains proper scroll 
    // and auto-deselects on completion
    authCodeChanged(changeEvent) {
        let newCode = changeEvent.target.value.replace(
            /[^0-9]/g, "").substring(
            0, Constants.AUTH_CODE_LENGTH)
        this.setState({
            authCode: newCode
        });
        if (newCode.length >= 
                Constants.AUTH_CODE_LENGTH) {
            document.activeElement.blur();
            this.authCodeRef.current.scrollLeft = 0;
            this.login(newCode, null);
        }
    }

    render() {
        if (this.state.enteringAuthCode) {
            return (
                <div id="LoginPane" className={
                    `Pane BoxShadow ContentButtonContainer 
                    ${this.props.deactivated ?
                        "Deactivated" : ""
                     }`}>
                    <div className="VerticalContainer">
                        <div className="FormElement TextEntry">
                            <span className="EntryLabel">
                                Secret Code:</span>
                            <input type="text" name="AuthCodeInput" 
                                className={`TextInput AuthCodeInput ${
                                    this.state.errorMsg ? 
                                    "InvalidInput" : ""}`}
                                maxLength={
                                    `${Constants.AUTH_CODE_LENGTH}`}
                                value={this.state.authCode}
                                ref={this.authCodeRef}
                                onFocus={() => this.setState({
                                    authCode: ""})}
                                onChange={
                                    this.authCodeChanged.bind(
                                    this)}
                                onKeyDown={domEvent =>
                                    this.setState({
                                        escapePressed: 
                                            domEvent.keyCode === 
                                            Constants.ESCAPE_KEY
                                    })}
                                onKeyUp={this.login.bind(this, null)}
                            />
                        </div>
                    </div>
                    <div className="FormElement">
                        <div className={`FormButton BoxShadow ${
                                this.state.escapePressed ?
                                "Pressed" : ""}`}
                            onClick={() => this.setState({
                                authCode: "",
                                enteringAuthCode: false
                            })} >
                            back
                        </div>
                    </div>
                </div>
            );
        } else {
            return (
                <div id="LoginPane" className={
                    `Pane BoxShadow ContentButtonContainer 
                    ${this.props.deactivated ?
                        "Deactivated" : ""
                     }`}>
                    <div className="VerticalContainer">
                        <div className="FormElement TextEntry">
                            <span className="EntryLabel">
                                Phone Number:</span>
                            <PhoneInput id="PhoneNumberInput" 
                                country={'us'} 
                                value={this.state.phoneNumber} 
                                onChange={
                                    phoneNumber => this.setState({
                                        phoneNumber
                                    })
                                }
                                containerClass="" 
                                inputClass=""
                            />
                        </div>
                        <div className="FormElement TextEntry">
                            <span className="EntryLabel">
                                Pass Word:</span>
                            <input type="pwd" id="PasswordInput"
                                name="PasswordInput" 
                                className={`TextInput ${
                                    this.state.errorMsg ? 
                                    "InvalidInput" : ""}`}
                                value={this.state.password}
                                onChange={changeEvent => 
                                    this.setState({
                                        password: 
                                            changeEvent.target.value
                                    })}
                                onKeyDown={domEvent =>
                                    this.setState({
                                        enterPressed: 
                                            domEvent.keyCode === 
                                            Constants.ENTER_KEY,
                                        escapePressed: 
                                            domEvent.keyCode === 
                                            Constants.ESCAPE_KEY
                                    })}
                                onKeyUp={this.login.bind(this, null)}
                            />
                        </div>
                        <div className="FormElement CheckEntry">
                            <span className="CheckLabel">
                                Remember This User Forever?
                            </span>
                            <input type="checkbox" id="RememberInput"
                                checked={this.state.remember}
                                className="CheckInput"
                                onChange={() => this.setState({
                                    remember: !this.state.remember
                                })}
                            />
                        </div>
                    </div>
                    <div className="FormElement">
                        <div className={`FormButton BoxShadow ${
                                this.state.enterPressed ?
                                "Pressed" : ""}`}
                            onClick={this.login.bind(this, null)}>
                            get secret code
                        </div>
                    </div>
                </div>
            );
        }
    }
}

export default LoginPane;
