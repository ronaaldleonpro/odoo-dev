# -*- coding: utf-8 -*-

import json
from odoo import _, api, fields, models, modules

class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def _get_activity_groups(self):
        """ Obtener grupos de actividades para Scope Management en el systray """
        activity_groups = super()._get_activity_groups()
        
        # Filtrar y obtener actividades específicas de scope management
        query = """
            SELECT count(*), act.res_model, act.res_id,
                   CASE
                       WHEN %(date)s - act.date_deadline::date = 0 THEN 'today'
                       WHEN %(date)s - act.date_deadline::date > 0 THEN 'overdue'
                       WHEN %(date)s - act.date_deadline::date < 0 THEN 'planned'
                   END AS states
             FROM mail_activity AS act
            WHERE act.res_model = 'scope.management' 
              AND act.user_id = %(user_id)s 
              AND act.active in (TRUE, %(active)s)
         GROUP BY states, act.res_model, act.res_id
        """
        
        self.env.cr.execute(query, {
            'date': str(fields.Date.context_today(self)),
            'user_id': self.env.uid,
            'active': self._context.get('active_test', True),
        })
        
        activity_data = self.env.cr.dictfetchall()
        view_type = getattr(self.env['scope.management'], '_systray_view', False)

        # Crear grupo de actividades para Scope Management
        scope_activities = {
            'id': self.env['ir.model']._get('scope.management').id,
            'name': _('Scope Management'),
            'model': 'scope.management',
            'type': 'activity',
            'icon': '/scope_management/static/description/icon.png',  # Ajustar ruta del icono
            'total_count': 0, 
            'today_count': 0, 
            'overdue_count': 0, 
            'planned_count': 0,
            'res_ids': set(),
            'view_type': view_type,
        }

        # Procesar datos de actividades
        for activity in activity_data:
            scope_activities['res_ids'].add(activity['res_id'])
            scope_activities[f"{activity['states']}_count"] += activity['count']
            if activity['states'] in ('today', 'overdue'):
                scope_activities['total_count'] += activity['count']

        # Agregar dominio de filtro
        if scope_activities['res_ids']:
            scope_activities.update({
                'domain': json.dumps([['id', 'in', list(scope_activities['res_ids'])]])
            })
            activity_groups.append(scope_activities)

        return activity_groups