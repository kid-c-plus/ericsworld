import React from "react";
import PhoneInput from 'react-phone-input-2';

import Constants from "./constants.js";

// React component for phone number update subpane
class PhoneNumberUpdateSubpane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            phoneNumber:    "",
            password:       "",
            authCode:       "",
            
            enteringAuthCode:   false

            errorMsg:   null
        };

        this.authCodeRef = React.createRef();
    }

    // bound function to submit entered information and either
    // change number or prompt for 2FA auth on new device
    update(domEvent) {
        // on clicks and Enter keypress
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === 13) {
            let body = {
                phone_number:   `+${this.state.phoneNumber}`,
                password:       this.state.password
            };
            if (this.state.enteringAuthCode) {
                body["auth_code"] = this.state.authCode;
                this.props.updatePhoneNumber(
                    body, null);
            } else {
                this.props.csrfFetch(
                    Constants.UPDATE_NUMBER_ENDPOINT,
                    {
                        method:         "POST",
                        credentials:    "include",
                        body:           JSON.stringify(body)
                    })
                .then(response => {
                    if (response.status === 204) {
                        this.setState({enteringAuthCode: true});
                    }
                    return response.json()
                }).then(errorResp => {
                    if ("error" in errorResp) {
                        this.setState(
                            {errorMsg: errorResp["error"]}
                        );
                    }
                });
            }
        }
    }

    // 

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
        }
    }
    
    render() {
        let form = <>< />;   
        if (this.state.enteringAuthCode) {
            form = (<div className="FormElement TextEntry">
                <span className="EntryLabel">Secret Code:</span>
                <input type="text" name="AuthCodeInput" 
                    className="TextInput AuthCodeInput"
                    maxLength={`${Constants.AUTH_CODE_LENGTH}`}
                    value={this.state.authCode}
                    ref={this.authCodeRef}
                    onFocus={() => this.setState({
                        authCode: ""})}
                    onChange={this.authCodeChanged.bind(this)}
                    onKeyUp={this.update.bind(this)}
                />
            </div>);
        } else {
            form = (<div className="VerticalContainer">
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
            </div>);
        }
        return (
            <div id="PhoneNumberUpdateSubpane"
                className="Subpane ContentButtonContainer">
                {form}
                <div className="HorizontalContainer">
                    <div className="FormElement Half">
                        <div className="FormButton BoxShadow"
                            onClick={this.cancel.bind(this)}>
                            cancel
                        </div>
                    </div>
                    <div className="FormElement Half">
                        <div className="FormButton BoxShadow"
                            onClick={this.update.bind(this)}>
                            {this.state.enteringAuthCode ?
                            "get secret code" : "update"}
                        </div>
                    </div>
                </div>
            </div
    }
}

export default PhoneNumberUpdateSubpane;
