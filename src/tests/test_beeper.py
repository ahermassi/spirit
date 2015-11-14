from __future__ import division
import time
try:
    from unittest import mock
except ImportError:
    import mock

from geometry_msgs.msg import PoseStamped
import pygame
import pytest
import rospy

import beeper


@pytest.fixture(scope="session")
def pygame_teardown():
    def fin():
        pygame.quit()


class TestTrackingVerifier(object):
    def setup(self):
        self.timeout = 5e-4
        beeper.TIMEOUT = self.timeout
        rospy.init_node("beeper_test", anonymous=True)
        self.beeper = beeper.TrackingVerifier()

    def create_pose(self):
        pose = PoseStamped()
        pose.header.stamp = rospy.Time.now()
        return pose

    def make_steady_state(self):
        pose = self.create_pose()
        pose.pose.position.x = 1
        self.beeper.callback(pose)
        pose = self.create_pose()
        self.beeper.callback(pose)

    @mock.patch.object(beeper.TrackingVerifier, "beep", autospec=True)
    def test_changing_pose_steady_state(self, mock_beep):
        self.make_steady_state()

        for i in range(21):
            pose = self.create_pose()
            pose.pose.position.x = i
            self.beeper.callback(pose)
            time.sleep(self.timeout / 10)

        assert not mock_beep.called
        assert self.beeper.tracking
        assert self.beeper.last_updated == pose.header.stamp

    @mock.patch.object(beeper.TrackingVerifier, "beep", autospec=True)
    def test_not_changing_pose_steady_state(self, mock_beep):
        self.make_steady_state()
        last_change_time = self.beeper.last_updated

        for i in range(21):
            self.beeper.callback(self.create_pose())
            time.sleep(self.timeout / 10)

        assert mock_beep.called
        assert not self.beeper.tracking
        assert self.beeper.last_updated == last_change_time

    @mock.patch.object(beeper.TrackingVerifier, "beep", autospec=True)
    def test_tracking_reacquired_steady_state(self, mock_beep):
        self.make_steady_state()
        self.beeper._tracking = False

        time.sleep(self.timeout / 10)
        pose = self.create_pose()
        pose.pose.position.x = 1
        self.beeper.callback(pose)

        assert not mock_beep.called
        assert self.beeper.tracking

    @mock.patch.object(beeper.TrackingVerifier, "beep", autospec=True)
    def test_changing_pose_at_start(self, mock_beep):
        pose = self.create_pose()
        self.beeper.callback(pose)

        assert not mock_beep.called
        assert self.beeper.tracking is None
        assert self.beeper.last_updated is None

        time.sleep(self.timeout / 10)
        pose = self.create_pose()
        pose.pose.position.x = 1
        self.beeper.callback(pose)

        assert not mock_beep.called
        assert self.beeper.tracking
        assert self.beeper.last_updated == pose.header.stamp

    @mock.patch.object(beeper.TrackingVerifier, "beep", autospec=True)
    def test_not_changing_pose_at_start(self, mock_beep):
        pose = self.create_pose()
        self.beeper.callback(pose)

        for i in range(21):
            self.beeper.callback(self.create_pose())
            time.sleep(self.timeout / 10)

        assert not mock_beep.called
        assert self.beeper.tracking is False
        assert self.beeper.last_updated is None

    @mock.patch.object(beeper.TrackingVerifier, "beep", autospec=True)
    def test_tracking_reacquired_after_bad_start(self, mock_beep):
        pose = self.create_pose()
        self.beeper.callback(pose)

        for i in range(21):
            self.beeper.callback(self.create_pose())
            time.sleep(self.timeout / 10)

        time.sleep(self.timeout / 10)
        pose = self.create_pose()
        pose.pose.position.x = 1
        self.beeper.callback(pose)

        assert not mock_beep.called
        assert self.beeper.tracking

    @mock.patch.object(beeper.TrackingVerifier, "beep", autospec=True)
    def test_empty_pose(self, mock_beep):
        self.beeper.callback(None)

        assert not mock_beep.called
        assert self.beeper.tracking is None
        assert self.beeper.last_updated is None
