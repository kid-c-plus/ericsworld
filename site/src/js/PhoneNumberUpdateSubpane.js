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

            errorMsg:   null,

            // true while enter is pressed, for rendering button
            enterPressed:   false,
            // likewise with escape, for cancel button
            escapePressed:  false
        };

        this.authCodeRef = React.createRef();
    }

    // bound function to submit entered information and either
    // change number or prompt for 2FA auth on new device
    update(authCode, domEvent) {
        // on clicks and Enter keypress
        this.setState({
            enterPressed:   false,
            escapePressed:  false
        });
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === Constants.ENTER_KEY) {
            let body = {
                new_number:   `+${this.state.phoneNumber}`,
                password:       this.state.password
            };
            if (this.props.enteringAuthCode) {
                if (authCode !== null) {
                    body["auth_code"] = authCode;
                } else {
                    body["auth_code"] = this.state.authCode;
                }
            }

            this.props.updatePhoneNumber(
                body, domEvent);
        } else if (domEvent.keyCode === Constants.ESCAPE_KEY) {
            this.cancel(null);
        }
    }

    // bound function to cancel - either clears set phone number
    // or returns to parent, depending on state
    cancel(domEvent) {
        if (this.props.enteringAuthCode) {
            this.setState({
                phoneNumber:        "",
                password:           "",
                authCode:           "",
                enteringAuthCode:   false
            });
        } else {
            this.props.cancel();
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
            this.update(newCode, null);
        }
    }
    
    render() {
        let form = <>< />;   
        if (this.props.enteringAuthCode) {
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
                        onKeyDown={domEvent =>
                            this.setState({
                                enterPressed: 
                                    domEvent.keyCode === 
                                    Constants.ENTER_KEY,
                                escapePressed: 
                                    domEvent.keyCode === 
                                    Constants.ESCAPE_KEY
                            })} 
                        onKeyUp={this.update.bind(this, null)}
                    />
                </div>
                <div className="HorizontalContainer">
                    <div className="FormElement">
                        <div className={`FormButton BoxShadow ${
                                this.state.escapePressed ?
                                "Pressed" : ""}`}
                            onClick={this.props.cancel}>
                            cancel
                        </div>
                    </div>
                </div>
            </ >);
        } else {
            form = (<>
                <div className="VerticalContainer">
                    <div className="FormElement TextEntry">
                        <span className="EntryLabel">
                            New Number:
                        </span>
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
                        <span className="EntryLabel">Pass Word:</span>
                        <input type="pwd" id="PasswordInput"
                            name="PasswordInput" className="TextInput"
                            value={this.state.password}
                            onChange={changeEvent => this.setState({
                                password: changeEvent.target.value
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
                            onKeyUp={this.update.bind(this, null)}
                        />
                    </div>
                </div>
                <div className="HorizontalContainer">
                    <div className="FormElement Half">
                        <div className={`FormButton BoxShadow ${
                                this.state.escapePressed ?
                                "Pressed" : ""}`}
                            onClick={this.props.cancel}>
                            cancel
                        </div>
                    </div>
                    <div className="FormElement Half">
                        <div className={`FormButton BoxShadow ${
                                this.state.enterPressed ?
                                "Pressed" : ""}`}
                            onClick={this.update.bind(this, null)}>
                            get code
                        </div>
                    </div>
                </div>
            </ >);
        }
        return (
            <div id="PhoneNumberUpdateSubpane"
                className="Subpane ContentButtonContainer">
                {form}
                
            </div>
        );
    }
}

export default PhoneNumberUpdateSubpane;
