import Ember from "ember";
import ENV from "../config/environment";


export default Ember.Controller.extend({
  currentVersion: ENV.APP.currentVersion,
  userId: function() {
    if (this.get("session.isAuthenticated") && this.get("session.content.token")) {
      var data = JSON.parse(atob(this.get("session.content.token").split(".")[1]));
      return data.uln?(data.ufn+" "+data.uln):data.ufn;
    } else {
      return "Unknown User";
    }
  }.property("session.isAuthenticated")
});
