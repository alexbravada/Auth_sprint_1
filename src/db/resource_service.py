from datetime import datetime

import sqlalchemy.orm

from db.pg_base import PostgresService
from models.user_model import Role, Resource, ResourceRole
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from flask import abort

from utils.orm_wraps import engine_session


class ResourceService(PostgresService):
    def __init__(self):
        super().__init__()

    @engine_session()
    def check_permissions_role_resource(self, role_id: int, resource_uuid: str, resource_type: str,
                                        session: sqlalchemy.orm.Session = None) -> dict:
        try:
            session.query(Role).filter(Role.id == role_id).one()
            resource_row = session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                          Resource.resource_type == resource_type).one()
        except NoResultFound:
            abort(404)
        else:
            permissions_row = session.query(ResourceRole).filter(
                ResourceRole.role_id == role_id,
                ResourceRole.resource_id == resource_row.id).one()
            return {'resource': resource_row.as_dict,
                    'permissions': permissions_row.as_dict}

    @engine_session()
    def create_resource(self, resource_uuid, resource_type, resource_name: str = None, role_id: int = 1,
                        can_create: bool = False,
                        can_read: bool = False,
                        can_update: bool = False,
                        can_delete: bool = False, session: sqlalchemy.orm.Session = None) -> dict:

        try:
            session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                           Resource.resource_type == resource_type).one()
        except NoResultFound:
            resource = Resource(resource_uuid=resource_uuid, name=resource_name, resource_type=resource_type)
            session.add(resource)
            session.commit()
            resource = session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                      Resource.resource_type == resource_type).one()
            permission = ResourceRole(resource_id=resource.id,
                                      role_id=role_id,
                                      can_create=can_create,
                                      can_read=can_read,
                                      can_update=can_update,
                                      can_delete=can_delete)
            session.add(permission)
            session.commit()
            resource = session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                      Resource.resource_type == resource_type).one()
            permissions = session.query(ResourceRole).filter(ResourceRole.resource_id == resource.id).one()
            return {'resource': resource.as_dict,
                    'permissions': permissions.as_dict}

        else:
            abort(400)

    @engine_session()
    def show_resource(self, resource_id: int = None, resource_uuid: str = None, resource_type: str = None,
                      resource_name: str = None, session: sqlalchemy.orm.Session = None) -> dict | list[dict]:
        def by_id() -> dict:
            try:
                session.query(Resource).filter(Resource.id == resource_id).one()
            except NoResultFound:
                abort(404)
            else:
                return session.query(Resource).filter(Resource.id == resource_id).one().as_dict

        def by_uuid_type() -> dict:
            try:
                session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                               Resource.resource_type == resource_type).one()
            except NoResultFound:
                abort(404)
            else:
                return session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                      Resource.resource_type == resource_type).one().as_dict

        def by_uuid_name() -> dict:
            try:
                session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                               Resource.name == resource_name).one()
            except NoResultFound:
                abort(404)
            else:
                return session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                      Resource.name == resource_name).one().as_dict

        def by_type() -> list[dict]:
            try:
                session.query(Resource).filter(Resource.resource_type == resource_type).all()
            except NoResultFound:
                abort(404)
            else:
                return [x.as_dict for x in
                        session.query(Resource).filter(Resource.resource_type == resource_type).all()]

        if resource_id:
            return by_id()
        elif resource_uuid and resource_type:
            return by_uuid_type()
        elif resource_uuid and resource_name:
            return by_uuid_name()
        elif resource_type and not resource_uuid and not resource_id:
            return by_type()
        else:
            return [x.as_dict for x in session.query(Resource).all()]

    @engine_session()
    def update_resource(self, resource_uuid: str = None, resource_type: str = None, resource_id: int = None,
                        new_uuid: str = None,
                        new_type: str = None,
                        new_name: str = None,
                        session: sqlalchemy.orm.Session = None) -> dict:
        def by_uuid_type() -> dict:
            try:
                resource_row = session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                              Resource.resource_type == resource_type).one()
            except NoResultFound:
                abort(404)
            else:
                res_id = session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                    Resource.resource_type == resource_type).one().as_dict
                res_id = res_id.get('id')
                session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                               Resource.resource_type == resource_type).update(
                    {
                        'resource_uuid': new_uuid if new_uuid else resource_row.resource_uuid,
                        'resource_type': new_type if new_type else resource_row.resource_type,
                        'name': new_name if new_name else resource_row.name,
                        'modified': datetime.utcnow() if new_uuid or new_type or new_name else None
                    }
                )
                session.commit()
                return session.query(Resource).filter(Resource.id == res_id).one().as_dict

        def by_id() -> dict:
            try:
                resource_row = session.query(Resource).filter(Resource.id == resource_id).one()
            except NoResultFound:
                abort(404)
            else:
                session.query(Resource).filter(Resource.id == resource_id).update(
                    {
                        'resource_uuid': new_uuid if new_uuid else resource_row.resource_uuid,
                        'resource_type': new_type if new_type else resource_row.resource_type,
                        'name': new_name if new_name else resource_row.name,
                        'modified': datetime.utcnow() if new_uuid or new_type or new_name else None
                    }
                )
                session.commit()
                return session.query(Resource).filter(Resource.id == resource_id).one().as_dict

        if resource_id:
            return by_id()
        if resource_uuid and resource_type:
            return by_uuid_type()
        else:
            abort(400)

    @engine_session()
    def delete_resource(self, resource_uuid: str = None, resource_type: str = None, resource_id: int = None,
                        session: sqlalchemy.orm.Session = None) -> dict:
        def by_uuid_type() -> dict:
            try:
                session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                               Resource.resource_type == resource_type).one()
            except NoResultFound:
                abort(404)
            else:
                res_row = session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                     Resource.resource_type == resource_type).one().as_dict

                count = session.query(Resource).filter(Resource.resource_uuid == resource_uuid,
                                                       Resource.resource_type == resource_type).delete()
                if count == 1:
                    session.commit()
                    return res_row
                else:
                    abort(500)

        def by_id() -> dict:
            try:
                session.query(Resource).filter(Resource.id == resource_id).one()
            except NoResultFound:
                abort(404)
            else:
                res_row = session.query(Resource).filter(Resource.id == resource_id).one().as_dict

                count = session.query(Resource).filter(Resource.id == resource_id).delete()
                if count == 1:
                    session.commit()
                    return res_row
                else:
                    abort(500)

        if resource_id:
            return by_id()
        elif resource_uuid and resource_type:
            return by_uuid_type()
        else:
            abort(400)
