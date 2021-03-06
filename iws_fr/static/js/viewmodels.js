// Activate Sugar js library to extend js objects with awesome functions.
Sugar.extend();

// ViewModels shared between different pages.
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
    ko.computed(function () {
        if (self.comments().length > 0) {
            $.getJSON(
                '/api/comment/' + self.comments().max('created').id(),
                function (data) {
                    // TODO: Map user?
                    var localDate = moment.parseZone(data.created).local();
                    self.lastModifiedBy(data.user.full_name);
                    self.lastModifiedDateAbsolute(localDate);
                    self.lastModifiedDateRelative(localDate.fromNow());
                }
            );
        } else {
            var localDate = moment.parseZone(self.created()).local();
            self.lastModifiedBy(self.user().fullName);
            self.lastModifiedDateAbsolute(localDate);
            self.lastModifiedDateRelative(localDate.fromNow());
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
