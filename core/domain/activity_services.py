# coding: utf-8
#
# Copyright 2016 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Commands for operating on lists of activity references."""

import logging

from core.domain import activity_domain
from core.platform import models
import feconf
(activity_models,) = models.Registry.import_models([models.NAMES.activity])


def get_featured_activity_references():
    featured_model_instance = (
        activity_models.ActivityReferencesModel.get_or_create(
            activity_models.ACTIVITY_REFERENCE_LIST_FEATURED))

    return [
        activity_domain.ActivityReference(reference['type'], reference['id'])
        for reference in featured_model_instance.activity_references]


def update_featured_activity_references(featured_activity_references):
    """Updates the current list of featured activity references.

    This assumes that the input is a list of activity references corresponding
    to publicly-viewable activities.
    """
    for activity_reference in featured_activity_references:
        activity_reference.validate()

    activity_hashes = [
        reference.get_hash() for reference in featured_activity_references]
    if len(activity_hashes) != len(set(activity_hashes)):
        raise Exception(
            'The activity reference list should not have duplicates.')

    featured_model_instance = (
        activity_models.ActivityReferencesModel.get_or_create(
            activity_models.ACTIVITY_REFERENCE_LIST_FEATURED))
    featured_model_instance.activity_references = [
        reference.to_dict() for reference in featured_activity_references]
    featured_model_instance.put()


def remove_featured_activity(activity_type, activity_id):
    featured_references = get_featured_activity_references()

    activity_reference_found = False
    new_activity_references = []
    for reference in featured_references:
        if reference.type != activity_type or reference.id != activity_id:
            new_activity_references.append(reference)
        else:
            activity_reference_found = True

    if activity_reference_found:
        # It is quite unusual for a featured activity to be unpublished or
        # deleted, so we log a message.
        logging.info(
            'The %s with id %s was removed from the featured list.' % (
                activity_type, activity_id))
        update_featured_activity_references(new_activity_references)


def split_by_type(activity_references):
    """Given a list of activity references, returns two lists: the first list
    contains the exploration ids, and the second contains the collection ids.
    The elements in each of the returned lists are in the same order as those
    in the input list.

    If any activity reference is incorrectly formatted, this raises an
    Exception.
    """
    exploration_ids, collection_ids = [], []
    for activity_reference in activity_references:
        if activity_reference.type == feconf.ACTIVITY_TYPE_EXPLORATION:
            exploration_ids.append(activity_reference.id)
        elif activity_reference.type == feconf.ACTIVITY_TYPE_COLLECTION:
            collection_ids.append(activity_reference.id)
        else:
            raise Exception(
                'Invalid activity reference: (%s, %s)' %
                (activity_reference.type, activity_reference.id))

    return exploration_ids, collection_ids
