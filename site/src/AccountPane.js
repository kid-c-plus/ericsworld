import React from "react";
import Constants from "./constants.js";
import AccountUpdatePane from "./AccountUpdatePane.js";
import LoginPane from "./LoginPane.js";

// React component for "account" pane. Renders either "login"
// or "update" component depending on login state
class AccountPane extends React.Component {
    render() {
        if (this.props.accountInfo) {
            return (
                <AccountUpdatePane accountInfo={
                        this.props.accountInfo}
                    csrfFetch={this.props.csrfFetch}
                    updateCallback={
                        this.props.accountUpdateCallback}
                    profileEditorCallback={
                        this.props.profileEditorCallback}
                    deactivateCallback={
                        this.props.deactivateCallback}
                    deactivated={this.props.deactivated}
                />
            );
        } else {
            return (
                <LoginPane 
                    csrfFetch={this.props.csrfFetch}
                    updateCallback={
                        this.props.accountUpdateCallback}
                    deactivateCallback={
                        this.props.deactivateCallback}
                    deactivated={this.props.deactivated}
                />
            );
        }
    }
}

export default AccountPane;
