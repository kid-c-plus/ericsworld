import React from "react";
import Constants from "./constants.js";

import "./WispPostPane.css";

// Root component for Wisp creation pane
class WispPostPane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            // Wisp component currently being edited
            // Right now, either "text" or "gif"
            focus:  "text",

            text:       "",
            gifUri:     "",

            errorMsg:   ""
        }

        this.textAreaRef = React.createRef();

        this.lineHeight = parseFloat(getComputedStyle(document.body)
            .getPropertyValue("--pvpratio"))
            * Constants.WISP_EDIT_LINE_HEIGHT;
        console.log(this.lineHeight);

        // track last scrollTop for textArea, to determine scroll
        // direction
        this.lastScrollTop = 0;
    }

    // post the entered wisp - on success, deactivate
    // and refresh wisps, on failure, display failure message
    post() {
        let body = {
           text:    this.state.text,
           gif_uri: this.state.gifUri
        }
        this.props.csrfFetch(
            Constants.POST_WISP_ENDPOINT,
            {
                method:         "POST",
                credentials:    "include",
                body:           JSON.stringify(body)
            })
        .then(response => {
            if (response.status === 201) {
                this.props.deactivateCallback();
                setTimeout(
                    () => this.props.refreshCallback(),
                    500
                );
            }
            return response.json()
        }).then(errorResp => {
            if ("error" in errorResp) {
                this.setState({errorMsg: errorResp["error"]});
            }
            console.log(errorResp);
        }).catch(error => {
            console.log(`Error posting Wisp: ${error.message}`);
        })
    }

    updateText(changeEvent) {
        this.setState({
            text: changeEvent.target.value});
    }

    checkTextScroll() {
        if (this.textAreaRef.current && 
                this.textAreaRef.current.scrollTop !== 
                this.lastScrollTop) {
            let currScrollTop = this.textAreaRef.current.scrollTop;
            let remainder = currScrollTop % this.lineHeight;
            // check difference between current and former scrollTop
            // to determine scroll direction
            if (remainder !== 0) {
                if (currScrollTop > this.lastScrollTop) {
                    // set to floor(current) + lineHeight, where
                    // floor is modulo lineHeight
                    this.textAreaRef.current.scrollTop = (
                        currScrollTop - remainder + this.lineHeight);
                } else {
                    // set to floor(current)
                    this.textAreaRef.current.scrollTop = 
                        currScrollTop - remainder;
                }
            }
            this.lastScrollTop = this.textAreaRef.current.scrollTop
        }
    }

    render() {
        this.checkTextScroll();
        let editFocusElem = <></>;
        if (this.state.focus === "text") {
            editFocusElem = (
                <div id="WispTextInputContainer"> 
                    <textarea id="WispTextInput"
                        ref={this.textAreaRef}
                        onKeyUp={this.checkTextScroll.bind(this)}
                        onKeyDown={() => setTimeout(
                            this.checkTextScroll.bind(this), 10)}
                        autoComplete="off" autoCorrect="off" 
                        autoCapitalize="off" spellCheck="false"
                        name="WispTextInput" className="TextInput"
                        maxLength={`${Constants.MAX_WISP_LENGTH}`}
                        value={this.state.text}
                        onChange={changeEvent => this.setState({
                            text: changeEvent.target.value.replace(
                            "\n", "")})}
                    />
                </div>
            );
        } else if (this.state.focus === "gif") {
            editFocusElem = <GifSearchSubpane selectGif={
                gifUri => this.setState({
                    gifUri: gifUri,
                    focus:  "text"
                })}
            />;
        }
        return (
            <div id="WispPostPane" className={
                    `Pane BoxShadow ${this.props.deactivated ?
                        "Deactivated" : ""
                     }`}>
                <div id="EditSubpane">
                    <div id="TextSelectButton"
                            className={"WispEditSelectButton" +
                            (this.state.focus === "text" ? 
                            " selected" : "")}
                            onClick={domEvent => this.setState({
                                focus: "text"
                            })} >
                        <img alt="wisp text editor" 
                            className="WispEditSelectButtonImg"
                            src="assets/wisp_text_edit.gif" />
                        <span>text</span>
                    </div>
                    {editFocusElem}
                    <div id="GifSelectButton"
                            className={"WispEditSelectButton" +
                            (this.state.focus === "gif" ? 
                            " selected" : "")}
                            onClick={domEvent => this.setState({
                                focus: "gif"
                            })} >
                        <img alt="wisp gif editor" 
                            className="WispEditSelectButtonImg"
                            src="assets/wisp_gif_edit.gif" />
                        <span>pics</span>
                    </div>
                </div>
                    <div id="PostWispButton" 
                            className="FormButton BoxShadow" 
                            onClick={this.post.bind(this)}>
                        send wisp 
                    </div>
            </div>
        );
    }
};

class GifSearchSubpane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            gifSearch:  "",
            gifUris:    []
        }
    }

    searchGifs(domEvent) {
        if (this.state.gifSearch) {
            let params = new URLSearchParams();
            if (domEvent === null || domEvent._reactName === "onClick" ||
                    domEvent.keyCode === 13) {
                fetch(`${Constants.GIF_SEARCH_ENDPOINT}?${params}`, {
                    credentials: "include"
                })
            }
        }
    }

    render() {
        let gifImgs = this.state.gifUris.map(gifUri => (
            <img className="GifSearchImg" alt="gif search result"
                key={this.state.gifUri}
                src={`${Constants.Gif_ENDPOINT}/${gifUri}`}
                onClick={this.props.selectGif.bind(this)} />
        ));
        return (
            <div id="GifSearchSubpane">
                <div id="GifSearchBar">
                    <input type="text" id="GifSearchInput"
                        name="GifSearchInput"
                        className="TextInput"
                        value={this.state.gifSearch}
                        onChange={changeEvent => this.setState({
                            gifSearch: changeEvent.target.value})}
                        onKeyUp={this.searchGifs.bind(this)}
                    />
                    <div id="GifSearchButton" onClick={
                            this.searchGifs.bind(this)}>
                        <div id="GifSearchArrow" onClick={
                            this.searchGifs.bind(this)} />
                    </div>
                </div>
                <div id="GifSearchResultsSubpane">
                    {gifImgs}
                </div>
            </div>
        );
    }
};

export default WispPostPane;
