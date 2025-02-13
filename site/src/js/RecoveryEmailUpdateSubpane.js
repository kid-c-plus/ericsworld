import React from "react";

import Constants from "./constants.js";

// React component for updating email address of current account
class RecoveryEmailUpdateSubpane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            email:      this.props.recoveryEmail,
            password:   "",

            // true while enter is pressed, for rendering button
            enterPressed:   false,
            // likewise with escape, for cancel button
            escapePressed:  false
        }
    }

    // keyup and click handler for email update field
    // submits on button click and enter keypress
    submit(domEvent) {
        this.setState({
            enterPressed:   false,
            escapePressed:  false
        });
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === Constants.ENTER_KEY) {
            this.props.updateRecoveryEmail(
                {
                    "new_email":    this.state.email,
                    "password":     this.state.password
                }, null
            );
        } else if (domEvent.keyCode === Constants.ESCAPE_KEY) {
            this.props.cancel(null);
        } 
    }

    render() {
        return (
            <div id="RecoveryEmailUpdateSubpane" 
                className="Subpane ContentButtonContainer">
                <div className="VerticalContainer">
                    <div className="FormElement TextEntry">
                        <span className="EntryLabel">New Email:</span>
                        <input type="text" id="RecoveryEmailInput"
                            name="RecoveryEmailInput" 
                            className="TextInput"
                            maxLength={`${Constants.MAX_EMAIL_LENGTH}`}
                            value={this.state.email}
                            onChange={changeEvent => this.setState({
                                email: changeEvent.target.value
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
                            onKeyUp={this.submit.bind(this)}
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
                            onKeyUp={this.submit.bind(this)}
                        />
                    </div>
                </div>
                <div className="HorizontalContainer">
                    <div className="FormElement Half">
                        <div className={`FormButton BoxShadow ${
                                this.state.escapePressed ?
                                "Pressed" : ""}`}
                            onClick={this.props.cancel.bind(this)}>
                            cancel
                        </div>
                    </div>
                    <div className="FormElement Half">
                        <div className={`FormButton BoxShadow ${
                                this.state.enterPressed ?
                                "Pressed" : ""}`}
                            onClick={this.submit.bind(this)}>
                            update
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default RecoveryEmailUpdateSubpane;
