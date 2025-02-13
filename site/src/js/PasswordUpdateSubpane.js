import React from "react";

import Constants from "./constants.js";

// React component for updating password of current account
class PasswordUpdateSubpane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            currentPassword:    "",
            newPassword:        "",

            // true while enter is pressed, for rendering button
            enterPressed:   false,
            // likewise with escape, for cancel button
            escapePressed:  false
        }
    }

    // keyup and click handler for password update field
    // submits on button click and enter keypress
    submit(domEvent) {
        this.setState({
            enterPressed:   false,
            escapePressed:  false
        });
        if (domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === Constants.ENTER_KEY) {
            this.props.updatePassword(
                {
                    "current_password": this.state.currentPassword,
                    "new_password": this.state.newPassword
                }, null
            );
        } else if (domEvent.keyCode === Constants.ESCAPE_KEY) {
            this.props.cancel(null);
        } 
    }

    render() {
        return (
            <div id="PasswordUpdateSubpane" 
                className="Subpane ContentButtonContainer">
                <div className="VerticalContainer">
                    <div className="FormElement TextEntry">
                        <span className="EntryLabel">
                            Old Pass Word:
                        </span>
                        <input type="pwd" id="CurrentPasswordInput"
                            name="CurrentPasswordInput" 
                            className="TextInput"
                            value={this.state.currentPassword}
                            onChange={changeEvent => this.setState({
                                currentPassword: changeEvent.target.value
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
                        <span className="EntryLabel">
                            New Pass Word:
                        </span>
                        <input type="pwd" id="NewPasswordInput"
                            name="NewPasswordInput" 
                            className="TextInput"
                            value={this.state.newPassword}
                            onChange={changeEvent => this.setState({
                                newPassword: changeEvent.target.value
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

export default PasswordUpdateSubpane;
