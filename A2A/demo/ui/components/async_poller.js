import {
  LitElement,
  html,
} from 'https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js';

class AsyncPoller extends LitElement {
  static properties = {
    triggerEvent: {type: String},
    action: {type: Object},
    isRunning: {type: Boolean},
  };

  render() {
    return html`<div></div>`;
  }

  firstUpdated() {
    if (this.action) {
      setTimeout(() => {
        this.runTimeout(this.action)
      }, this.action.duration_seconds * 1000);
    }
  }

  runTimeout(action) {
    this.dispatchEvent(
      new MesopEvent(this.triggerEvent, {
        action: action,
      }),
    );
    setTimeout(() => {
      this.runTimeout(action);
    }, action.duration_seconds * 1000);
  }
}

customElements.define('async-action-component', AsyncPoller);
