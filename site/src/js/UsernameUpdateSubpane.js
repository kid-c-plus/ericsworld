import React from "react";

import Constants from "./constants.js";

// React component for updating username of current account
class UsernameUpdateSubpane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            username:   this.props.username,
            unique:     true,

            // true while enter is pressed, for rendering button
            enterPressed:   false,
            // likewise with escape, for cancel button
            escapePressed:  false
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
        this.setState({
            enterPressed:   false,
            escapePressed:  false
        });
        if ((domEvent === null || domEvent._reactName === "onClick" || 
                domEvent.keyCode === Constants.ENTER_KEY)
                && this.state.unique) {
            this.props.updateUsername(
                {"new_username": this.state.username}, null
            );
        } else if (domEvent.keyCode === Constants.ESCAPE_KEY) {
            this.props.cancel(null);
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
            <div id="UsernameUpdateSubpane" 
                className="Subpane ContentButtonContainer">
                <div className="VerticalContainer">
                    <div className="FormElement TextEntry">
                        <span className="EntryLabel">User Name:</span>
                        <input type="text" id="UsernameInput"
                            name="UsernameInput" className="TextInput"
                            maxLength={`${Constants.MAX_USERNAME_LENGTH}`}
                            value={this.state.username}
                            onChange={this.usernameChanged.bind(this)}
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
                    <div className="FormElement StatusReadout">
                        {uniqueStatus}
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

export default UsernameUpdateSubpane;
