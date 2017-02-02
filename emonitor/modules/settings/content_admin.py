import os
from flask import request, render_template, current_app, redirect
from emonitor.modules.settings.department import Department
from emonitor.modules.settings.settings import Settings
from emonitor.modules.streets.city import City
from emonitor.extensions import alembic, db, babel, scheduler
from emonitor.scheduler import eMonitorIntervalTrigger


def getAdminContent(self, **params):
    """
    Deliver admin content of module settings

    :param params: use given parameters of request
    :return: rendered template as string
    """
    module = request.view_args['module'].split('/')

    def chunks(l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]

    if len(module) == 2:
        if module[1] == 'department':  # department submodule
            if request.method == 'POST':
                if request.form.get('action') == 'savedept':  # save department
                    if request.form.get('dep_id') != 'None':  # update
                        department = Department.getDepartments(request.form.get('dep_id'))
                        l = request.form.get('dep_pos')
                    else:  # add
                        l = len(Department.getDepartments()) + 1
                        department = Department('', '', '', 0)
                        db.session.add(department)
                    department.name = request.form.get('dep_name')
                    department.shortname = request.form.get('dep_shortname')
                    department.color = request.form.get('dep_color')
                    department.set(u'address_name', unicode(request.form.get('dep_address_name')))
                    department.set(u'address_street', unicode(request.form.get('dep_address_street')))
                    department.set(u'address_city', unicode(request.form.get('dep_address_city')))
                    department.set(u'address_phone', unicode(request.form.get('dep_address_phone')))
                    department.set(u'address_fax', unicode(request.form.get('dep_address_fax')))
                    department.set(u'address_email', unicode(request.form.get('dep_address_email')))
                    if len(request.files) > 0:
                        uploadfile = request.files.get('dep_logo')
                        if uploadfile.filename != '':
                            _fname, _fext = os.path.splitext(uploadfile.filename)
                            db.session.flush()  # flush to get department id of new department
                            fname = os.path.join(current_app.config.get('PATH_DATA'), 'departmentlogo_{}{}'.format(department.id, _fext))
                            uploadfile.save(fname)
                            department.set(u'logo', u'departmentlogo_{}{}'.format(department.id, _fext))  # store relative path from data directory
                        elif request.form.get('logoaction') == 'deletelogo':
                            if os.path.exists('{}{}'.format(current_app.config.get('PATH_DATA'), department.attributes['logo'])):
                                os.remove('{}{}'.format(current_app.config.get('PATH_DATA'), department.attributes['logo']))
                                department.set(u'logo', u'')
                    department.orderpos = l
                    department.defaultcity = request.form.get('dep_city')
                    db.session.commit()
                    
                elif request.form.get('action') == 'createdepartment':  # add department
                    params.update({'department': Department('', '', '', 0), 'cities': City.getCities()})
                    return render_template('admin.settings.department_actions.html', **params)

                elif request.form.get('action').startswith('detaildept_'):  # edit department
                    params.update({'department': Department.getDepartments(id=request.form.get('action').split('_')[-1]), 'cities': City.getCities()})
                    return render_template('admin.settings.department_actions.html', **params)

                elif request.form.get('action').startswith('deletedept_'):  # delete department
                    _c = []
                    for city in City.getCities():
                        if city.department.id == int(request.form.get('action').split('_')[-1]):
                            _c.append(city.name)
                    if len(_c) == 0:
                        db.session.delete(Department.getDepartments(id=request.form.get('action').split('_')[-1]))
                        db.session.commit()
                    else:
                        params.update({'error': babel.gettext('admin.settings.department_deleteerror1', cities=', '.join(_c))})
                    
                elif request.form.get('action') == 'ordersetting':  # change department order
                    for _id in request.form.getlist('departmentids'):
                        Department.getDepartments(id=_id).orderpos = request.form.getlist('departmentids').index(_id) + 1
                    db.session.commit()
            
            params.update({'departments': Department.getDepartments(), 'cities': City.getCities()})
            return render_template('admin.settings.department.html', **params)

        elif module[1] == 'cars':
            if request.method == 'POST':
                if request.form.get('action') == 'updatetypes':
                    Settings.set('cartypes', [i for i in chunks(request.form.getlist('cartype'), 2) if i[0] != ''])
                    db.session.commit()
            params.update({'cartypes': Settings.getCarTypes()})
            return render_template('admin.settings.cars.html', **params)

        elif module[1] == 'communication':
            from emonitor.extensions import communication
            if request.method == 'POST':
                if request.form.get('action') == 'telegramsettings':
                    vals = Settings.get('telegramsettings', {})
                    vals['telegramkey'] = request.form.get('telegrambot').strip()
                    vals['welcomemsg'] = request.form.get('welcometext')
                    vals['helpmsg'] = request.form.get('helptext')
                    Settings.set('telegramsettings', vals)
                    db.session.commit()
                    tb = communication.telegram
                    if not tb:
                        communication.init_app(app=communication.app)
                        tb = communication.telegram
                    #else:
                     #   tb.stop()
                    try:
                        tb.updateToken(vals['telegramkey'])
                    except AttributeError:
                        pass

                elif request.form.get('action') == 'telegramgroups':
                    vals = Settings.get('telegramsettings', {})
                    g = {}
                    for f in filter(lambda x: x.startswith('groupname_'), request.form):
                        _id = f.split('_')[-1]  # fieldname in form
                        if request.form.get('groupname_' + _id) in ['newgroup', '']:
                            continue
                        g[request.form.get('groupname_' + _id)] = request.form.get('members_selectable_' + _id).split(';')
                    vals['groups'] = g
                    Settings.set('telegramsettings', vals)
                    db.session.commit()

            params.update({'bot': communication.telegram, 'settings': Settings.getYaml('telegramsettings'), 'configtelegramkey': current_app.config.get('TELEGRAMKEY', '')})
            return render_template('admin.settings.communication.html', **params)

        elif module[1] == 'start':

            if request.method == 'POST':
                if request.form.get('action') == 'updatestart':  # update start page definition
                    areas = dict()
                    areas['center'] = {'module': request.form.get('center.module'), 'width': '0', 'visible': 1}
                    areas['west'] = {'module': request.form.get('west.module'), 'moduleadd': request.form.getlist('west.module.add'), 'width': '.%s' % request.form.get('west.width'), 'visible': request.form.get('west.visible')}
                    areas['east'] = {'module': request.form.get('east.module'), 'moduleadd': request.form.getlist('east.module.add'), 'width': '.%s' % request.form.get('east.width'), 'visible': request.form.get('east.visible')}

                    Settings.set('frontend.default', areas)
                    db.session.commit()

            def modname(obj):  # get translation for sorting of module
                _t = "module.%s" % obj.info['name']
                return babel.gettext(_t)

            params.update({'mods': sorted([m for m in current_app.blueprints['frontend'].modules.values() if m.frontendContent() == 1], key=modname), 'center': Settings.getFrontendSettings('center'), 'west': Settings.getFrontendSettings('west'), 'east': Settings.getFrontendSettings('east')})
            return render_template('admin.settings.start.html', **params)

    else:

        if request.method == 'POST':  # save settings
            if request.form.get('action') == 'observerstate':
                Settings.set('observer.interval', request.form.get('observerinterval'))
                if 'observerinterval' in [j.name for j in scheduler.get_jobs()]:  # use file
                    _jobserver = scheduler.get_jobs('observerinterval')[0]
                    if Settings.get('observer.interval', '0') == '0':
                        _jobserver.pause()
                    else:
                        scheduler.reschedule_job(_jobserver.id, trigger=eMonitorIntervalTrigger(seconds=int(Settings.get('observer.interval', current_app.config.get('OBSERVERINTERVAL', 2)))))

            elif request.form.get('action') == 'monitorping':
                Settings.set('monitorping', request.form.get('monitorping'))
                _jping = scheduler.get_jobs('monitorping')[0]
                if Settings.get('monitorping', '0') == '0':
                    _jping.pause()
                else:
                    scheduler.reschedule_job(_jping.id, trigger=eMonitorIntervalTrigger(minutes=int(Settings.get('monitorping', current_app.config.get('MONITORPING', 2)))))

        paths = dict(pathdata=current_app.config.get('PATH_DATA'), pathtmp=current_app.config.get('PATH_TMP'), pathincome=current_app.config.get('PATH_INCOME'), pathdone=current_app.config.get('PATH_DONE'))
        params.update({'paths': paths, 'observerinterval': Settings.get('observer.interval', current_app.config.get('OBSERVERINTERVAL')), 'watchdog': 'observerinterval' not in [j.name for j in scheduler.get_jobs()], 'monitorping': Settings.get('monitorping', current_app.config.get('MONITORPING')), 'alarmsevalfields': Settings.get('alarms.evalfields'), 'alembic': alembic})
        return render_template('admin.settings.html', **params)
    return redirect("/admin/settings", code=302)


def getAdminData(self, **params):
    """
    Deliver admin content of module settings (ajax)

    :return: rendered template as string or json dict
    """
    if request.args.get('action') == 'checkpath':
        if os.path.exists(request.args.get('path')):
            return '1'
        return '0'

    elif request.args.get('action') == 'upgradedb':
        try:
            alembic.upgrade()
            return str(alembic.current())
        except:
            return babel.gettext(u'admin.settings.updatedberror')

    elif request.args.get('action') == 'downgradedb':
        return alembic.downgrade() or "done"

    elif request.args.get('action') == 'sendtelegramtest':
        from emonitor.extensions import communication
        communication.telegram.sendMessage(addressee=int(request.args.get('user')), message=request.args.get('msg'))
        return babel.gettext(u'admin.settings.telegramtest.done')

    return ""
