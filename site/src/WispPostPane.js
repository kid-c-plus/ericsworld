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

            gifSearch:  "",
            gifUris:    [],
            statusMsg:  "search for a beautiful gif...",
            gifScroll:  0,

            errorMsg:   "",
            
            // track whether enter is being held
            // so as to shade the button
            enterHeld:  false
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
                    1000
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

    
    // check the state of the Wisp text box and, if needed,
    // set it to be in line with the underlines
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

    // query the backend for the gif search string set in state
    // updates the "gifUris" state obj
    searchGifs(domEvent) {
        if (this.state.gifSearch) {
            let params = new URLSearchParams();
            params.append("term_string", this.state.gifSearch);
            if (domEvent === null || domEvent._reactName === "onClick" ||
                    domEvent.keyCode === 13) {
                fetch(`${Constants.GIF_SEARCH_ENDPOINT}?${params}`, {
                    credentials: "include"
                }).then(response => response.json())
                .then(gifResp => {
                    if ("gifs" in gifResp) {
                        this.setState({
                            gifUris:    gifResp["gifs"],
                            statusMsg: (
                                gifResp["gifs"].length > 0 ? 
                                "" : "no pics found :~(")
                        })
                    } else if ("error" in gifResp) {
                        this.setState(
                            {statusMsg: gifResp["error"]});
                    }
                }).catch(error => {
                    console.log(
                        `Error searching Gifs: ${error.message}`);
                })
            }
        }
    }

    // keyUp event handler for text - submits on Enter press, else
    // rechecks scroll level
    textKeyUp(keyEvent) {
        console.log(keyEvent.keyCode);
        if (keyEvent.keyCode === 13) {
            this.post();
        }
        this.checkTextScroll();
    }

    // keyDown event handler for text - sets EnterHeld and rechecks 
    // text Scroll after 5 ms timeout
    textKeyDown(keyEvent) {
        if (keyEvent.keyCode === 13) {
            this.setState({
                enterHeld : true
            });
        }
        setTimeout(this.checkTextScroll.bind(this), 5);
    }

    render() {
        this.checkTextScroll();
        let gifSearchResults = null;
        if (this.state.gifUris.length > 0) { 
            gifSearchResults = this.state.gifUris.map(gifUri => (
                <img alt="gif search result"
                    key={`search-${gifUri}`}
                    src={`${Constants.GIF_ENDPOINT}/${gifUri}`}
                    className={gifUri === this.state.gifUri ? 
                        "GifSearchImg Selected" : "GifSearchImg" }
                    onClick={domEvent => this.setState({
                        "gifUri": gifUri
                    })} />
            ));
            console.log(gifSearchResults);
        } else {
            gifSearchResults = (<div id="GifSearchStatus">
                {this.state.statusMsg}
            </div>);
        }

        let editFocusElems = (<>
            <div id="WispTextInputContainer" style={
                    this.state.focus === "text" ?
                    {} : {display: "none"}}>
                <textarea id="WispTextInput" 
                    ref={this.textAreaRef}
                    onKeyUp={this.textKeyUp.bind(this)}
                    onKeyDown={this.textKeyDown.bind(this)}
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
            <div id="GifSearchContainer" style={
                    this.state.focus === "gif" ?
                    {} : {display: "none"}}>
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
                <div id="GifSearchResultsContainer">
                    {gifSearchResults}
                </div>
            </div>
        </>);

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
                    {editFocusElems}
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
                            className={`FormButton BoxShadow ${
                                this.state.enterHeld ? "Pressed" : ""
                                }`} 
                            onClick={this.post.bind(this)}>
                        send wisp 
                    </div>
            </div>
        );
    }
};

export default WispPostPane;
