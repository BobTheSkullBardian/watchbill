from django.shortcuts import (
    # render,
    redirect,
)
from sailors.models import (
    # Sailor,
    create_sailor,
)
import os


def index(request):
    redirect('calendar/')
    # qs = Sailor.objects.order_by('name')
    # # print(qs)
    # context = {
    #     'sailors': qs,
    # }
    # return render(request, 'index.html', context)


def process(request):
    import pandas as pd
    import numpy as np
    file = request.FILES.get('file')
    # headers = [
    #     'rate',
    #     'name',
    #     # '_ord',
    #     'dnec',
    #     'ult',
    #     # 'ult_acc',
    #     # 'spi',
    #     'detatch_uic',
    #     'est_detatch_date',
    #     'act_detatch_date',
    #     'est_arrival_date',
    #     # 'view_orders',
    #     # 'pg_quest',
    #     # 'pg_info',
    #     'co_letter',
    #     'sponser_letter',
    #     'spouse_letter',
    #     'sponsor_contact',
    #     # 'modify_data',
    #     'accepted',
    #     'sponsor',
    #     # 'sponsor_agreement',
    #     # 'add_change',
    #     # 'notes',
    # ]

    filename, ext = os.path.splitext(file.name)
    if str(ext) == '.csv':
        data = pd.read_csv(
            file,
        ).fillna(np.nan).replace([np.nan], [None])
    elif str(ext)[:4] == '.xls':
        data = pd.read_excel(
            file,
        ).fillna(np.nan).replace([np.nan], [None])

    # data = pd.read_csv(
    #     file,
    #     # sheet_name="JOOD-DD",
    #     # names=headers,
    #     # usecols='A, B, D, E, H:K, O:R, T, U',  # , X',
    # ).fillna(np.nan).replace([np.nan], [None])

    log = {
        'Updated': [],
        'Created': [],
    }
    for _, sailor in data.iterrows():
        fullname = sailor['name'].split(',')
        lname = fullname[0]
        fname = (fullname[1].split(' '))[0]
        name = ', '.join([lname, fname])
        parsed = {
            'name': name,
            'phone': sailor['phone'],
            'email': sailor['email'],
            'rate': sailor['rate'],
            'report': sailor['act_arrival_date'],
        }
        clean = {}
        for k, v in parsed.items():
            if v:
                clean[k] = v

        if create_sailor(clean):
            log['Created'].append(name)
        else:
            log['Updated'].append(name)
    for k, v in log.items():
        print(f'{k}:')
        for sailor in v:
            print(f'\t{sailor}')
    return redirect('/')
