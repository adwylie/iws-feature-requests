import datetime
import os
import unittest
import random
import sys
import tempfile
from flask_fixtures import FixturesMixin
from sqlalchemy.exc import IntegrityError

from .settings import app
from .settings import db
from .models import (Client, Comment, FeatureRequest, ProductArea, User)

# Disable info logging in flask_fixtures library.
import logging
logging.disable(logging.INFO)


class FlaskTestCase(unittest.TestCase, FixturesMixin):
    fixtures = ['clients.json', 'productareas.json', 'users.json']
    app, db = app, db  # Required setup for fixtures to work.

    def setUp(self):
        app.testing = True
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        self.app = app.test_client()
        self.base_date = datetime.datetime.now() + datetime.timedelta(days=1)

        db.create_all()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    # Tests.
    def test_default_data(self):
        """Ensure fixtures can be loaded."""
        clients = Client.query.all()
        product_areas = ProductArea.query.all()
        users = User.query.all()

        assert len(clients) == Client.query.count() == 3
        assert len(product_areas) == ProductArea.query.count() == 4
        assert len(users) == User.query.count() == 7

    def test_feature_request_priority_range(self):
        """Ensure that FR's can only have a positive priority value."""
        # Bill Lumbergh attempts to create some FRs.
        common_values = {
            'user_id': 4,
            'client_id': 3,
            'target_date': self.base_date
        }

        negative_priority = FeatureRequest(
            title="Allow a user to enter 'notes' when transferring funds.",
            priority=random.randint(-sys.maxsize - 1, -2),
            **common_values
        )
        negative_one_priority = FeatureRequest(
            title='Separate display of pending and posted transactions.',
            priority=-1,
            **common_values
        )
        zero_priority = FeatureRequest(
            title='Allow free-form security questions.',
            priority=0,
            **common_values
        )
        one_priority_title = 'Store passwords as a hash instead of in plain-text format.'
        one_priority = FeatureRequest(
            title=one_priority_title,
            priority=1,
            **common_values
        )
        positive_priority_title = 'Allow social account login using OAuth 2.0.'
        positive_priority_value = random.randint(2, sys.maxsize)
        positive_priority = FeatureRequest(
            title=positive_priority_title,
            priority=positive_priority_value,
            **common_values
        )

        # Attempt to insert FRs.
        negative_exception = False
        try:
            self.db.session.add(negative_priority)
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
            negative_exception = True

        assert negative_exception

        negative_one_exception = False
        try:
            self.db.session.add(negative_one_priority)
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
            negative_one_exception = True

        assert negative_one_exception

        zero_exception = False
        try:
            self.db.session.add(zero_priority)
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
            zero_exception = True

        assert zero_exception

        self.db.session.add(one_priority)
        self.db.session.commit()

        saved_one_priority = FeatureRequest.query.filter_by(title=one_priority_title).one()
        assert saved_one_priority
        assert saved_one_priority.priority == 1

        self.db.session.add(positive_priority)
        self.db.session.commit()

        saved_positive_priority = FeatureRequest.query.filter_by(title=positive_priority_title).one()
        assert saved_positive_priority
        assert saved_positive_priority.priority == positive_priority_value

    def test_feature_request_priority_validation(self):
        """Ensure inserts/updates to FR priority works as it should."""
        # Insert some random FRs, then do an update or two. Check at each
        # step that the number of elements and their order is correct.

        # Insert at 5 (result: inserted)
        road_runner_title = 'Beep Beep'
        road_runner = FeatureRequest(
            user_id=6, client_id=2, title=road_runner_title,
            target_date=self.base_date, priority=5)
        self.db.session.add(road_runner)
        self.db.session.commit()

        assert FeatureRequest.query.count() == 1

        saved_road_runner = FeatureRequest.query.filter_by(priority=5).first()
        assert saved_road_runner
        assert saved_road_runner.title == road_runner_title

        # Insert at 2 (result: inserted, no other changes)
        bugs_bunny_title = 'Add Marking to Iron Carrot'
        bugs_bunny = FeatureRequest(
            user_id=7, client_id=2, title=bugs_bunny_title,
            target_date=self.base_date, priority=2)
        self.db.session.add(bugs_bunny)
        self.db.session.commit()

        assert FeatureRequest.query.count() == 2

        saved_bugs_bunny = FeatureRequest.query.filter_by(priority=2).first()
        assert saved_bugs_bunny
        assert saved_bugs_bunny.title == bugs_bunny_title

        saved_road_runner = FeatureRequest.query.filter_by(priority=5).first()
        assert saved_road_runner
        assert saved_road_runner.title == road_runner_title

        # Insert at 1 (result: inserted, no other changes)
        super_outfit_title = "Super Outfit Doesn't Grant Powers"
        super_outfit = FeatureRequest(
            user_id=5, client_id=2, title=super_outfit_title,
            target_date=self.base_date, priority=1)
        self.db.session.add(super_outfit)
        self.db.session.commit()

        assert FeatureRequest.query.count() == 3

        saved_super_outfit = FeatureRequest.query.filter_by(priority=1).first()
        assert saved_super_outfit
        assert saved_super_outfit.title == super_outfit_title

        saved_bugs_bunny = FeatureRequest.query.filter_by(priority=2).first()
        assert saved_bugs_bunny
        assert saved_bugs_bunny.title == bugs_bunny_title

        saved_road_runner = FeatureRequest.query.filter_by(priority=5).first()
        assert saved_road_runner
        assert saved_road_runner.title == road_runner_title

        # Now some erroneous inserts.
        giant_kite_title = 'Add German Instructions to Giant Kite Kit'
        giant_kite_base_opts = {
            'user_id': 5,
            'client_id': 2,
            'title': giant_kite_title,
            'target_date': self.base_date
        }

        # Insert at 0 (result: error)
        insert_exception = False
        try:
            giant_kite = FeatureRequest(**giant_kite_base_opts, priority=0)
            self.db.session.add(giant_kite)
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
            insert_exception = True

        assert insert_exception

        # Insert at -? (result: error)
        insert_exception = False
        try:
            giant_kite = FeatureRequest(
                **giant_kite_base_opts,
                priority=random.randint(-sys.maxsize - 1, -1)
            )
            self.db.session.add(giant_kite)
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
            insert_exception = True

        assert insert_exception

        # Insert at 1 (result: inserted, old 1+2 moved up, no other changes)
        giant_kite = FeatureRequest(**giant_kite_base_opts, priority=1)
        self.db.session.add(giant_kite)
        self.db.session.commit()

        assert FeatureRequest.query.count() == 4

        saved_giant_kite = FeatureRequest.query.filter_by(priority=1).first()
        assert saved_giant_kite
        assert saved_giant_kite.title == giant_kite_title

        saved_super_outfit = FeatureRequest.query.filter_by(priority=2).first()
        assert saved_super_outfit
        assert saved_super_outfit.title == super_outfit_title

        saved_bugs_bunny = FeatureRequest.query.filter_by(priority=3).first()
        assert saved_bugs_bunny
        assert saved_bugs_bunny.title == bugs_bunny_title

        saved_road_runner = FeatureRequest.query.filter_by(priority=5).first()
        assert saved_road_runner
        assert saved_road_runner.title == road_runner_title

        # Insert at 4 (result: inserted, no other changes)
        super_glue_title = 'Include Glue Remover With Super Glue'
        super_glue = FeatureRequest(
            user_id=5, client_id=2, title=super_glue_title,
            target_date=self.base_date, priority=4)
        self.db.session.add(super_glue)
        self.db.session.commit()

        assert FeatureRequest.query.count() == 5

        saved_giant_kite = FeatureRequest.query.filter_by(priority=1).first()
        assert saved_giant_kite
        assert saved_giant_kite.title == giant_kite_title

        saved_super_outfit = FeatureRequest.query.filter_by(priority=2).first()
        assert saved_super_outfit
        assert saved_super_outfit.title == super_outfit_title

        saved_bugs_bunny = FeatureRequest.query.filter_by(priority=3).first()
        assert saved_bugs_bunny
        assert saved_bugs_bunny.title == bugs_bunny_title

        saved_super_glue = FeatureRequest.query.filter_by(priority=4).first()
        assert saved_super_glue
        assert saved_super_glue.title == super_glue_title

        saved_road_runner = FeatureRequest.query.filter_by(priority=5).first()
        assert saved_road_runner
        assert saved_road_runner.title == road_runner_title

        # Update bugs bunny (priority 3) to have a priority of 1.
        saved_bugs_bunny.priority = 1
        self.db.session.commit()

        assert FeatureRequest.query.count() == 5

        saved_bugs_bunny = FeatureRequest.query.filter_by(priority=1).first()
        assert saved_bugs_bunny
        assert saved_bugs_bunny.title == bugs_bunny_title

        saved_giant_kite = FeatureRequest.query.filter_by(priority=2).first()
        assert saved_giant_kite
        assert saved_giant_kite.title == giant_kite_title

        saved_super_outfit = FeatureRequest.query.filter_by(priority=3).first()
        assert saved_super_outfit
        assert saved_super_outfit.title == super_outfit_title

        saved_super_glue = FeatureRequest.query.filter_by(priority=4).first()
        assert saved_super_glue
        assert saved_super_glue.title == super_glue_title

        saved_road_runner = FeatureRequest.query.filter_by(priority=5).first()
        assert saved_road_runner
        assert saved_road_runner.title == road_runner_title

    def test_feature_request_priority_default(self):
        """Ensure that FRs without priority are given lowest priority."""
        # Bill Lumbergh continues to attempt creating some FRs.
        common_values = {
            'user_id': 4,
            'client_id': 3,
            'target_date': self.base_date
        }
        fr1_title = 'Allow security answers to contain spaces.'
        fr1 = FeatureRequest(title=fr1_title, **common_values)

        fr2_title = "Add a 'keep me logged in' feature."
        fr2 = FeatureRequest(title=fr2_title, **common_values)

        self.db.session.add(fr1)
        self.db.session.commit()

        saved_fr1 = FeatureRequest.query.filter_by(title=fr1_title).one()
        assert saved_fr1
        assert saved_fr1.priority == 1

        self.db.session.add(fr2)
        self.db.session.commit()

        saved_fr2 = FeatureRequest.query.filter_by(title=fr2_title).one()
        assert saved_fr2
        assert saved_fr2.priority == 2

    def test_feature_request_target_date_validation(self):
        """Ensure that FRs cannot be created with a past target_date."""
        # Bill Lumbergh continues to attempt creating some FRs.
        common_values = {'user_id': 4, 'client_id': 3}

        # Past target date.
        past_exception = False
        try:
            FeatureRequest(
                title='Add RRSP account interface to web client.',
                target_date=datetime.datetime.now() - datetime.timedelta(days=1),
                **common_values
            )
        except ValueError:
            past_exception = True

        assert past_exception

        # Present target date.
        present_exception = False
        try:
            FeatureRequest(
                title='Add TFSA account interface to web client.',
                target_date=datetime.datetime.now(),
                **common_values
            )
        except ValueError:
            present_exception = True

        assert present_exception

        # Future target date.
        future_title = 'Add mortgage products interface to web client.'
        future = FeatureRequest(
            title=future_title,
            target_date=datetime.datetime.now() + datetime.timedelta(days=1),
            **common_values
        )

        self.db.session.add(future)
        self.db.session.commit()

        saved_future = FeatureRequest.query.filter_by(title=future_title).one()
        assert saved_future

    def test_feature_request_identifier_increment(self):
        """Test that when inserting a FeatureRequest its 'identifier' is set."""
        # Wile E. Coyote has some issues with ACME products.
        dynamite_fr_title = 'Add Pause Function to Dynamite Timer.'
        dynamite_fr = FeatureRequest(
            user_id=5,
            client_id=2,
            title=dynamite_fr_title,
            description='Static fuse length does not handle all situations, '
                        'and is unsafe if apparatus changes are required after '
                        'countdown begins.',
            priority=1,
            target_date=self.base_date
        )
        boulders_fr_title = 'Allow varying water requirement to Dehydrated Boulders.'
        boulders_fr = FeatureRequest(
            user_id=5,
            client_id=2,
            title=boulders_fr_title,
            description='Instead of fixed water requirement for a specific '
                        'boulder size, allow amount of water to determine '
                        'boulder size.',
            priority=2,
            target_date=self.base_date
        )
        invalid_fr = FeatureRequest(
            user_id=5,
            client_id=2,
            identifier=2,  # Incorrect identifier since inserted third.
            title="An invalid feature request.",
            priority=3,
            target_date=self.base_date
        )
        roller_skates_fr_title = 'Improve braking on rocked-powered roller skates.'
        roller_skates_fr = FeatureRequest(
            user_id=5,
            client_id=2,
            identifier=3,  # Correct identifier since inserted third.
            title=roller_skates_fr_title,
            description="Current skates don't even have brakes, how this "
                        "product passed safety standards is beyond me.",
            priority=3,
            target_date=self.base_date
        )

        # FRs inserted without identifiers should have them added automatically.
        # The client_id + priority relation is unique, so we'll query by that
        # to check correct object saving.
        self.db.session.add(dynamite_fr)
        self.db.session.commit()

        saved_dynamite = FeatureRequest.query.filter_by(client_id=2, priority=1).one()
        assert saved_dynamite.title == dynamite_fr_title
        assert saved_dynamite.identifier == 1

        self.db.session.add(boulders_fr)
        self.db.session.commit()

        saved_boulders = FeatureRequest.query.filter_by(client_id=2, priority=2).one()
        assert saved_boulders.title == boulders_fr_title
        assert saved_boulders.identifier == 2

        # FR with incorrect identifier should throw error.
        exception = False
        try:
            self.db.session.add(invalid_fr)
            self.db.session.commit()
        except IntegrityError:
            self.db.session.rollback()
            exception = True

        assert exception

        # FR with correct (pre-incremented ) identifier should bo okay.
        self.db.session.add(roller_skates_fr)
        self.db.session.commit()

        saved_roller_skates = FeatureRequest.query.filter_by(client_id=2, priority=3).one()
        assert saved_roller_skates.title == roller_skates_fr_title
        assert saved_roller_skates.identifier == 3

        # TODO: shouldn't be able to add identifier with space below it.

    def test_feature_request_comment_created_default(self):
        """Test that the FeatureRequest and Comment 'created' fields are set."""
        # Michael Bolton creates first FR for Initech, no product areas.
        fr = FeatureRequest(
            user_id=3,
            client_id=3,
            identifier=1,
            title='Convert 2-digit dates to 4-digit.',
            description='Prepare for Y2K by updating date storage format',
            priority=1,
            target_date=self.base_date
        )

        # Bill Lumbergh replies in his typical way.
        comment = Comment(user_id=4, feature_request_id=4,
                          text="Hello Michael, what's happening? Just make"
                          "sure to get the cover sheets on the TPS reports.")

        # Set up, test the results.
        self.db.session.add(fr)
        self.db.session.add(comment)
        self.db.session.commit()

        saved_fr = FeatureRequest.query.filter_by(client_id=3, identifier=1).one()
        saved_comment = Comment.query.filter_by(user_id=4, feature_request_id=4).one()

        assert saved_fr.created
        assert saved_comment.created

    def test_user_full_name(self):
        """Test that the User.full_name property works."""
        bill_id = 4
        bill_full_name = 'Bill Lumbergh'

        bill = User.query.get(bill_id)

        assert bill
        assert bill.full_name == bill_full_name
        assert bill == User.query.filter_by(full_name=bill_full_name).one()


if '__main__' == __name__:
    unittest.main()
