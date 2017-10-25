Sugar.extend();

// TODO: Move view models out to own file, gets loaded before individual page js.
function ProductArea(data) {
    var self = this;

    self.id = ko.observable();
    self.name = ko.observable();

    ko.mapping.fromJS(data, ProductArea.mapping, self);
}
ProductArea.mapping = {};

function User(data) {
    var self = this;

    // TODO: Mapping with different name?
    self.id = ko.observable();
    self.firstName = ko.observable(data.first_name);
    self.lastName = ko.observable(data.last_name);
    self.fullName = ko.observable(data.full_name);

    ko.mapping.fromJS(data, User.mapping, self);
}
User.mapping = {};

function Client(data) {
    var self = this;

    self.id = ko.observable();
    self.name = ko.observable();

    ko.mapping.fromJS(data, Client.mapping, self);
}
Client.mapping = {};

function Comment(data) {
    var self = this;

    self.id = ko.observable();
    self.user = ko.observable();
    self.text = ko.observable();
    self.created = ko.observable();

    ko.mapping.fromJS(data, Comment.mapping, self);
}
Comment.mapping = {
    user: {
        create: function (options) {
            return new User(options.data);
        },
        key: function (data) {
            return ko.utils.unwrapObservable(data.id);
        }
    }
};

function FeatureRequest(data) {
    var self = this;

    // TODO: Mapping with different name?
    self.id = ko.observable();
    self.user = ko.observable();
    self.client = ko.observable();
    self.identifier = ko.observable();
    self.slug = ko.observable();
    self.title = ko.observable();
    self.description = ko.observable();
    self.priority = ko.observable();
    self.targetDate = ko.observable(data.target_date);
    self.created = ko.observable();

    self.comments = ko.observableArray();
    self.productAreas = ko.observableArray(data.product_areas);

    self.lastModifiedBy = ko.observable();
    self.lastModifiedDateAbsolute = ko.observable();
    self.lastModifiedDateRelative = ko.observable();

    // TODO: General: When do I use the parentheses to call observables?
    ko.computed(function() {
        if (self.comments().length > 0) {
            $.getJSON(
                '/api/comment/' + self.comments().max('created').id(),
                function (data) {
                    // TODO: Map user?
                    var date = new Date(data.created);

                    self.lastModifiedBy(data.user.full_name);
                    self.lastModifiedDateAbsolute(date.long());
                    self.lastModifiedDateRelative(date.relative());
                }
            );
        } else {
            // TODO: Set proper locale.
            var date = new Date(self.created());

            self.lastModifiedBy(self.user().fullName);
            self.lastModifiedDateAbsolute(date.long());
            self.lastModifiedDateRelative(date.relative());
        }
    });

    ko.mapping.fromJS(data, FeatureRequest.mapping, self);
}
FeatureRequest.mapping = {
    user: {
        create: function (options) {
            return new User(options.data);
        },
        key: function (data) {
            return ko.utils.unwrapObservable(data.id);
        }
    },
    client: {
        create: function (options) {
            return new Client(options.data);
        },
        key: function (data) {
            return ko.utils.unwrapObservable(data.id);
        }
    },
    comments: {
        create: function (options) {
            return new Comment(options.data);
        },
        key: function (data) {
            return ko.utils.unwrapObservable(data.id);
        }
    }
};

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
