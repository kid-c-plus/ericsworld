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

            errorMsg:   ""
        };

        this.authCodeRef = React.createRef();
    }

    login(domEvent) {
        // on clicks and Enter keypress
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === 13) {
            let body = {
                phone_number:   `+${this.state.phoneNumber}`,
                password:       this.state.password
            }
            if (this.state.enteringAuthCode) {
                body["auth_code"] = this.state.authCode;
                body["remember"] = this.state.remember;
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
                } else if (response.status === 204) {
                    this.setState({enteringAuthCode: true});
                }
                return response.json()
            }).then(errorResp => {
                if ("error" in errorResp) {
                    this.setState({errorMsg: errorResp["error"]});
                }
                console.log(errorResp);
            }).catch(error => {
                console.log(`Error logging in: ${error.message}`);
            })
        }
    }

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
        }
    }

    render() {
        let form = <>< />;
        if (this.state.enteringAuthCode) {
            form = (<>
                <div className="FormElement TextEntry">
                    <span className="EntryLabel">Secret Code:</span>
                    <input type="text" name="AuthCodeInput" 
                        className="TextInput AuthCodeInput"
                        maxLength={`${Constants.AUTH_CODE_LENGTH}`}
                        value={this.state.authCode}
                        ref={this.authCodeRef}
                        onFocus={() => this.setState({
                            authCode: ""})}
                        onChange={this.authCodeChanged.bind(this)}
                        onKeyUp={this.login.bind(this)}
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
                <div className="FormElement">
                    <div className="FormButton BoxShadow" onClick={
                            this.login.bind(this)}>
                        login
                    </div>
                </div>
            < />);
        } else {
            form = (<>
                <div className="FormElement TextEntry">
                    <span className="EntryLabel">Phone Number:</span>
                    <PhoneInput id="PhoneNumberInput" country={'us'} 
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
                    <span className="EntryLabel">Pass Word:</span>
                    <input type="pwd" id="PasswordInput"
                        name="PasswordInput" className="TextInput"
                        value={this.state.password}
                        onChange={changeEvent => this.setState({
                            password: changeEvent.target.value
                        })}
                        onKeyUp={this.login.bind(this)}
                    />
                </div>
                <div className="FormElement">
                    <div className="FormButton BoxShadow" onClick={
                            this.login.bind(this)}>
                        get secret code
                    </div>
                </div>
            < />);
        }
        return (
            <div id="LoginPane" className={
                    `Pane BoxShadow ${this.props.deactivated ?
                        "Deactivated" : ""
                     }`}>
                {form}
            </div>
        );
    }
}

export default LoginPane;
