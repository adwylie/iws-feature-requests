function FeatureRequests(data) {
    var self = this;

    self.loaded = ko.observable(false);

    self.featureRequests = ko.observableArray();

    ko.mapping.fromJS(data, FeatureRequests.mapping, self);
}
FeatureRequests.mapping = {
    featureRequests: {
        create: function (options) {
            return new FeatureRequest(options.data);
        }
    }
};

var timeout;
var pollingRate = 5000;

var featureRequests = ko.mapping.fromJS({ featureRequests: []}, FeatureRequests.mapping);
ko.applyBindings(featureRequests);

// TODO: finish gui: need fr view + edit + new + delete
// TODO: filter by company
// TODO: priority update
// TODO: post trigger get update
var updateFeatureRequests = function () {
    var callback = function(data) {
        ko.mapping.fromJS({ featureRequests: data.objects }, featureRequests);
        timeout = setTimeout(updateFeatureRequests, pollingRate);
    };

    var queryParams = JSON.stringify({
       'order_by': [
           {'field': 'client_id', 'direction': 'asc'},
           {'field': 'priority', 'direction': 'asc'}
       ]
    });
    $.getJSON('/api/feature_request', {'q': queryParams}, callback);
};

updateFeatureRequests();
