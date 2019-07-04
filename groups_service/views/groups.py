'''Implementation groups_service''' # pylint: disable=cyclic-import
from sqlalchemy.exc import OperationalError, DataError
from flask import request, jsonify
from groups_service import APP
from groups_service.db import DB
from groups_service.serializers import (
    GROUP_SCHEMA,
    GROUPS_SCHEMA
)
from groups_service.models.group import GroupsModel


@APP.route('/api/create_group', methods=['POST'])
def post_group():
    """Post method for Group."""
    title = request.json['title']
    form_id = request.json['form_id']
    owner_id = request.json['owner_id']
    members = request.json['members']

    members = ",".join(map(str, members))
    # exists_group = None
    try:
        exists_group = GroupsModel.query.filter_by(
            title=title,
            form_id=form_id,
            owner_id=owner_id,
            members=members
            ).first()
    except DataError:
        return jsonify({'error':"input data not valid"}), 400
    message = jsonify({'message': 'Group alredy exists'}), 400
    if not exists_group:
        new_group = GroupsModel(title, form_id, owner_id, members)
        DB.session.add(new_group)
        try:
            DB.session.commit()
            message = GROUP_SCHEMA.jsonify(new_group), 201
        except OperationalError:
            message = jsonify({'error':'database are not responsing'}), 400
    return message

@APP.route('/api/groups', methods=['GET'])
def all_groups():
    """Get method for all groups."""
    try:
        groups = GroupsModel.query.all()
    except OperationalError:
        return jsonify({'message':'database are not responsing'})
    for group in groups:
        group.members = list(map(int, group.members.split(',')))
    message = GROUPS_SCHEMA.jsonify(groups)
    return message

@APP.route('/api/group/<group_id>')
def get_group(group_id):
    """Get method for one group by group_id."""
    if group_id.isnumeric():
        try:
            group = GroupsModel.query.get_or_404(group_id)
        except OperationalError:
            return jsonify({'message':'database are not responsing'})
        group.members = list(map(int, group.members.split(',')))
        message = GROUP_SCHEMA.jsonify(group)
    else:
        message = jsonify({'message': 'Not correct URL'}), 400
    return message

@APP.route('/api/groups/<owner_id>', methods=['GET'])
def get_groups_owner(owner_id):
    '''Get method for all groups by owner_id'''
    if owner_id.isnumeric():
        try:
            groups = GroupsModel.query.filter_by(owner_id=owner_id)
        except OperationalError:
            return jsonify({'message':'database are not responsing'})
        for group in groups:
            group.members = list(map(int, group.members.split(',')))
        message = GROUPS_SCHEMA.jsonify(groups)
    else:
        message = jsonify({'message': 'Not correct URL'})
    return message
