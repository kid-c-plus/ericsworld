import React from "react";
import Constants from "./constants.js";

// React component for individual Wisp
class Wisp extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            // whether the user has manually Hearted this Wisp
            // useful in order to avoid unnecessary queries to 
            // hearted-wisps endpoint
            manuallyHearted:    false,
            manuallyUnHearted:  false
        };
    }

    // bound function to set unHearted Wisp to Hearted, or vice
    // versa
    toggleWispHeart() {
        // UnHeart Hearted Wisp
        if (this.props.hearted || this.props.manuallyHearted) {
            this.setState({
                manuallyHearted:    false,
                manuallyUnHearted:  true
            });
            let body = {
                wisp_id:    this.props.data["wisp_id"]
            }
            this.props.csrfFetch(
                Constants.UNHEART_WISP_ENDPOINT, {
                    method:         "POST",
                    credentials:    "include",
                    body:           JSON.stringify(body)
            }).then(response => {
                if (response.status !== 200) {
                    this.setState({manuallyUnHearted: false});
                }
                console.log(response.json());
            });
        } else {
            this.setState({
                manuallyHearted:    true,
                manuallyUnHearted:  false
            });
            let body = {
                wisp_id:    this.props.data["wisp_id"]
            }
            this.props.csrfFetch(
                Constants.HEART_WISP_ENDPOINT, {
                    method:         "POST",
                    credentials:    "include",
                    body:           JSON.stringify(body)
            }).then(response => {
                if (response.status !== 200) {
                    this.setState({manuallyHearted: false});
                }
                console.log(response.json());
            });
        }
    }

    render() {
        return (
            <div className="Wisp BoxShadow">
                <div className="WispUserBox">
                    <div className="WispUserProfile">
                        <img className="WispUserProfileImg BoxShadow" 
                            alt="user profile"
                            src={
                                (`${Constants.PROFILE_ENDPOINT}/` +
                                this.props.data["user_profile_uri"])
                            } />
                    </div>
                </div>
                <div className="WispTextBox">
                    <div className="WispUserName">
                        {this.props.data["user_username"]}
                    </div>
                    <div className="WispText">
                        {this.props.data["text"]}
                    </div>
                    { this.props.data["gif_uri"] !== "" ? 
                        <div className="WispGif">
                            <img className="WispImg" 
                                alt="wisp attachment"
                                src={
                                    (`${Constants.GIF_ENDPOINT}/` +
                                    this.props.data["gif_uri"])
                                } />
                        </div>
                    : <></> }
                </div>
                <div className="WispHeartBox">
                    <div className="WispHeart">
                        {this.props.heartable ? 
                            <img className="WispHeartImg"
                                onClick={
                                    this.toggleWispHeart.bind(this)}
                                src={(this.props.hearted || 
                                    this.state.manuallyHearted) &&
                                    !this.state.manuallyUnHearted ? 
                                    "../assets/heart.png" : 
                                    "../assets/unheart.png"} 
                            /> : <> < />}
                    </div>
                </div>
            </div>
        );
    }
}

export default Wisp;
