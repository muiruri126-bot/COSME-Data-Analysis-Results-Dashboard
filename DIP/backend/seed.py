"""Seed the results framework from Gannt_Chart.docx data and create default roles/permissions."""
from models import (
    db, Role, Permission, BudgetHolder, User,
    IntermediateOutcome, ImmediateOutcome, Output, Activity, ScheduleFlag,
    role_permissions
)


def seed_roles_and_permissions():
    """Create default roles and permissions."""
    roles_data = [
        ('Admin', 'Full system access: manage users, roles, framework, settings'),
        ('ME_Specialist', 'Full create/edit/report across all entities + dashboards'),
        ('Budget_Holder', 'View portfolio; approve baselines; manage tasks under own portfolio'),
        ('Implementer', 'Create/update assigned tasks; comment; attach evidence'),
        ('Viewer', 'Read-only dashboards + exports'),
    ]

    resources = [
        'intermediate_outcome', 'immediate_outcome', 'output', 'activity',
        'task', 'comment', 'attachment', 'dashboard', 'report', 'baseline',
        'audit_log', 'user',
    ]
    actions = ['create', 'read', 'update', 'delete', 'approve', 'export']

    # Create permissions
    perm_map = {}
    for resource in resources:
        for action in actions:
            p = Permission.query.filter_by(resource=resource, action=action).first()
            if not p:
                p = Permission(resource=resource, action=action)
                db.session.add(p)
                db.session.flush()
            perm_map[(resource, action)] = p

    # Create roles
    role_map = {}
    for name, desc in roles_data:
        r = Role.query.filter_by(name=name).first()
        if not r:
            r = Role(name=name, description=desc)
            db.session.add(r)
            db.session.flush()
        role_map[name] = r

    # Assign permissions to roles
    admin_perms = [(res, act) for res in resources for act in actions]  # all

    me_perms = [(res, act) for res in resources for act in actions
                if not (res == 'user' and act in ('create', 'update', 'delete'))]

    bh_perms = [
        *[(res, 'read') for res in resources],
        ('activity', 'create'), ('activity', 'update'),
        ('task', 'create'), ('task', 'update'),
        ('comment', 'create'), ('comment', 'update'),
        ('attachment', 'create'), ('attachment', 'delete'),
        ('report', 'export'), ('dashboard', 'read'),
        ('baseline', 'create'),
    ]

    impl_perms = [
        *[(res, 'read') for res in ['intermediate_outcome', 'immediate_outcome', 'output', 'activity', 'task', 'dashboard']],
        ('task', 'create'), ('task', 'update'),
        ('comment', 'create'), ('comment', 'update'),
        ('attachment', 'create'), ('attachment', 'delete'),
    ]

    viewer_perms = [
        *[(res, 'read') for res in resources if res != 'audit_log'],
        ('report', 'export'), ('dashboard', 'read'),
    ]

    assignments = {
        'Admin': admin_perms,
        'ME_Specialist': me_perms,
        'Budget_Holder': bh_perms,
        'Implementer': impl_perms,
        'Viewer': viewer_perms,
    }

    for role_name, perms in assignments.items():
        role = role_map[role_name]
        role.permissions = []
        for resource, action in perms:
            if (resource, action) in perm_map:
                role.permissions.append(perm_map[(resource, action)])

    db.session.commit()
    return role_map


def seed_budget_holders():
    """Create budget holders."""
    names = ['Caro', 'Mwanzia', 'Jenard', 'Lilian', 'Benard', 'Agneta', 'Beryl']
    bh_map = {}
    for name in names:
        bh = BudgetHolder.query.filter_by(name=name).first()
        if not bh:
            bh = BudgetHolder(name=name)
            db.session.add(bh)
            db.session.flush()
        bh_map[name] = bh
    db.session.commit()
    return bh_map


def seed_default_admin(role_map):
    """Create default admin user."""
    admin = User.query.filter_by(email='admin@cosme-dip.org').first()
    if not admin:
        admin = User(
            email='admin@cosme-dip.org',
            full_name='System Admin',
        )
        admin.set_password('Admin@2026!')
        admin.roles.append(role_map['Admin'])
        db.session.add(admin)
        db.session.commit()
    return admin


def seed_results_framework():
    """Seed the full results framework hierarchy from Gannt_Chart.docx."""

    framework = [
        # (code, description, type, parent_code, status, schedule_flags)
        # Intermediate Outcome 1100
        ('1100', 'Enhanced adoption of gender-responsive and socially inclusive nature-based solutions (NbS) for climate change adaptation with biodiversity and ecosystem integrity co-benefits', 'intermediate_outcome', None, None, None),

        # Immediate Outcome 1110
        ('1110', 'Increased capacity of communities, especially women, to undertake gender-responsive and equitable mangrove restoration and conservation with biodiversity co-benefits', 'immediate_outcome', '1100', None, None),

        # Output 1111
        ('1111', 'Biodiversity assessment for mangrove restoration conducted', 'output', '1110', None, None),
        ('1111.1', 'Map mangrove and other coastal forest ecosystems (current and potential)', 'activity', '1111', None, [('Q1',)]),
        ('1111.2', 'Conduct biodiversity assessment on mangroves ecosystems in target communities', 'activity', '1111', None, [('Q1',)]),

        # Output 1112
        ('1112', 'Members of mangrove groups trained and coached in mangrove restoration, conservation', 'output', '1110', None, None),
        ('1112.1', 'Identify mangrove groups (current and potential) to be trained in mangrove management, conservation', 'activity', '1112', None, [('Q1',)]),
        ('1112.2', 'Conduct TNA (technical needs assessment) and opportunities on mangrove restoration, conservation and technical and capacity needs of mangrove groups', 'activity', '1112', None, [('Q1',)]),
        ('1112.3', 'Develop/tailor content for training on mangrove restoration, conservation', 'activity', '1112', None, [('Q1',)]),
        ('1112.4', 'Provide ToT on mangrove restoration, conservation', 'activity', '1112', None, [('Q1',)]),
        ('1112.5', 'Train mangrove groups on restoration and conservation', 'activity', '1112', None, [('W1',), ('W3', 'refresher')]),
        ('1112.6', 'Provide follow-up and ongoing mentorship support', 'activity', '1112', None, [('W1',), ('W2',), ('W3',)]),

        # Output 1113
        ('1113', 'Mangrove groups equipped with restoration and conservation inputs', 'output', '1110', None, None),
        ('1113.1', 'Support mangrove groups to become formally registered Beach Management Units and Community Forest Associations', 'activity', '1113', None, [('Q1',)]),
        ('1113.2', 'Provide inputs for mangrove restoration and conservation to mangrove groups', 'activity', '1113', None, [('W1',), ('W2',)]),

        # Immediate Outcome 1120
        ('1120', 'Increased capacity of women-led cooperatives to undertake regenerative and sustainable seaweed production, value addition and commercialization', 'immediate_outcome', '1100', None, None),

        # Output 1121
        ('1121', 'Gendered market and environmental assessment, and research into improved seaweed varietals conducted', 'output', '1120', None, None),
        ('1121.1', 'Review cultural and environmental context for local seaweed cultivation and farm site suitability', 'activity', '1121', None, [('Q1',)]),
        ('1121.2', 'Undertake research and development into the most locally relevant climate-resilient seaweed varietals and biobank', 'activity', '1121', None, [('Q1',)]),
        ('1121.3', 'Undertake gendered local and export market analysis (current and new markets) and value addition opportunities (soap, detergent, biostimulant, food, livestock feed)', 'activity', '1121', None, [('W1',), ('W2',)]),
        ('1121.4', 'Develop and distribute one-year outlook tide table', 'activity', '1121', None, [('W1',), ('W2',), ('W3',)]),

        # Output 1122
        ('1122', 'Women-led seaweed groups trained in seaweed production, value addition and commercialization', 'output', '1120', None, None),
        ('1122.1', 'Identify women-led seaweed groups', 'activity', '1122', None, [('Q1',)]),
        ('1122.2', 'Develop and adapt training materials on seaweed production, value addition and commercialization (business plans, finance management, links to financial services, local grants, etc.)', 'activity', '1122', None, [('Q1',)]),
        ('1122.3', 'Conduct ToT on seaweed production, value addition and commercialization', 'activity', '1122', None, [('Q1',)]),
        ('1122.4', 'Conduct training for women-led groups on seaweed production, value addition and commercialization', 'activity', '1122', None, [('W1',), ('W2',), ('W3', 'refresher')]),
        ('1122.5', 'Provide follow-up and ongoing mentorship support', 'activity', '1122', None, [('W1',), ('W2',), ('W3',)]),

        # Output 1123
        ('1123', 'Women-led seaweed groups provided with inputs to sustain or improve seaweed production', 'output', '1120', None, None),
        ('1123.1', 'Undertake needs assessment of equipment and supplies for existing seaweed groups', 'activity', '1123', None, [('Q1',)]),
        ('1123.2', 'Provide inputs to women-led seaweed groups to sustain or improve seaweed production', 'activity', '1123', None, [('W1',), ('W2',)]),
        ('1123.3', 'Develop nursery to support biobank and seaweed groups', 'activity', '1123', None, [('W1',), ('W2',)]),
        ('1123.4', 'Develop sustainable mechanism for groups\' access to biobank', 'activity', '1123', None, [('W1',), ('W2',)]),

        # Output 1124
        ('1124', 'High-capacity women-led seaweed groups supported through innovation pilots for crop resilience, yield improvement, or value-addition', 'output', '1120', None, None),
        ('1124.1', 'Identify women-led seaweed groups with capacity to participate in innovation pilots', 'activity', '1124', None, [('W1',), ('W2',)]),
        ('1124.2', 'Develop innovations for crop resilience, yield improvement, or value-addition and establish methods for piloting with selected women-led seaweed groups', 'activity', '1124', None, [('Q1',)]),
        ('1124.3', 'Implement innovation pilots with selected women-led seaweed groups and provide training in monitoring and maintenance to relevant stakeholders', 'activity', '1124', None, [('W1',), ('W2',), ('W3',)]),
        ('1124.4', 'Document and disseminate lessons learned to women-led groups and relevant stakeholders', 'activity', '1124', None, [('W2',), ('W3',)]),

        # Immediate Outcome 1130
        ('1130', 'Increased capacity of communities, especially women, to undertake gender-responsive, locally-led forest management and conservation', 'immediate_outcome', '1100', None, None),

        # Output 1131
        ('1131', 'Targeted local communities, especially women, trained in gender-responsive forest management and community-centred conservation', 'output', '1130', None, None),
        ('1131.1', 'Lead sensitization sessions on gender-focused conservation for local authorities', 'activity', '1131', None, [('Q1',)]),
        ('1131.2', 'Develop locally relevant and gender-responsive training content on sustainable forest regeneration, enrichment planting, forest product harvesting, and wildfire management', 'activity', '1131', None, [('Q1',)]),
        ('1131.3', 'Conduct locally relevant and gender-sensitive training sessions with forest conservation groups on gender-focused conservation for local authorities and target communities', 'activity', '1131', None, [('W1',), ('W3', 'refresher')]),

        # Output 1132
        ('1132', 'Targeted local women\'s groups supported to promote and pilot NbS based on forestry, including patrols and governance structures for gender responsive forest management & community-centred conservation', 'output', '1130', None, None),
        ('1132.1', 'Facilitate gender-responsive actions on sustainable forest regeneration, enrichment planting, and wildfire management to target community groups (at least 60% women)', 'activity', '1132', None, [('W1',), ('W2',), ('W3',)]),
        ('1132.2', 'Promote local community members, especially women, in governance structures and forest management decision-making', 'activity', '1132', None, [('W1',), ('W2',), ('W3',)]),
        ('1132.3', 'Increase community-led forest monitoring and patrols led by local authorities', 'activity', '1132', None, [('W1',), ('W2',), ('W3',)]),

        # ── Intermediate Outcome 1200 ──
        ('1200', 'Increased agency of women in their diversity to exercise their right to participate in gender-responsive, nature-based solutions with biodiversity co-benefits to increase adaptive capacity and build household and community resilience', 'intermediate_outcome', None, None, None),

        # Immediate Outcome 1210
        ('1210', 'Increased knowledge and skills of women on gender responsive NbS, economic rights, life skills, & GE&I', 'immediate_outcome', '1200', None, None),

        # Output 1211
        ('1211', 'Targeted women trained on gender responsive NbS, economic rights, life skills, & GE&I, including UPCW', 'output', '1210', None, None),
        ('1211.1', 'Develop and adapt content for training on climate change, economic rights, life skills, & GE&I', 'activity', '1211', None, [('Q1',)]),
        ('1211.2', 'Provide ToT on climate change, economic rights, life skills, & GE&I', 'activity', '1211', None, [('W1',), ('W2', 'refresher')]),
        ('1211.3', 'Conduct trainings and provide coaching on climate change, economic rights, life skills, & GE&I with women', 'activity', '1211', None, [('W1',), ('W2',), ('W3',)]),
        ('1211.4', 'Facilitate peer to peer learning exchanges among targeted women', 'activity', '1211', None, [('W2',), ('W3',)]),
        ('1211.5', 'Provide post-training support and follow-up support, including referrals (peer support - trained facilitators - referral for cases of GBV etc.)', 'activity', '1211', None, [('W1',), ('W2',), ('W3',)]),

        # Immediate Outcome 1220
        ('1220', 'Increased access to resilience building assets and opportunities for women', 'immediate_outcome', '1200', None, None),

        # Output 1221
        ('1221', 'Women\'s savings groups established or strengthened', 'output', '1220', None, None),
        ('1221.1', 'Map existing SGs and identify communities for new groups', 'activity', '1221', None, [('Q1',)]),
        ('1221.2', 'Review and adapt SG materials', 'activity', '1221', None, [('Q1',)]),
        ('1221.3', 'Provide supplies to new and existing SGs on a needs basis (box, passbook, stamps)', 'activity', '1221', None, [('Q1',)]),
        ('1221.4', 'Train community-based trainers (CBTs) as facilitators on SG methodologies', 'activity', '1221', None, [('Q1',)]),
        ('1221.5', 'Roll out SGs and deliver foundational training', 'activity', '1221', None, [('W1',), ('W2',)]),
        ('1221.6', 'Provide regular monitoring and support to SGs', 'activity', '1221', None, [('W1',), ('W2',), ('W3', 'refresher')]),
        ('1221.7', 'Create linkages with financial institutions to offer credit facilities to women', 'activity', '1221', None, [('W2',), ('W3',)]),

        # Output 1222
        ('1222', 'Women-led demonstration plots on regenerative agriculture supported', 'output', '1220', None, None),
        ('1222.1', 'Identify shared land for demonstration plots', 'activity', '1222', None, [('W1',), ('W2',)]),
        ('1222.2', 'Develop and adapt training materials on regenerative agriculture', 'activity', '1222', None, [('W1',), ('W2',)]),
        ('1222.3', 'Identify and train facilitators for the training', 'activity', '1222', None, [('W1',), ('W2',)]),
        ('1222.4', 'Deliver training to targeted households on regenerative agriculture', 'activity', '1222', None, [('W1',), ('W2',), ('W3', 'refresher')]),
        ('1222.5', 'Provide rainwater harvesting and drip-irrigation solutions to demonstration plots', 'activity', '1222', None, [('W1',), ('W2',)]),
        ('1222.6', 'Provide input support such as seeds, nature fertilizer, farm tools for crop production', 'activity', '1222', None, [('W1',), ('W2',), ('W3',)]),
        ('1222.7', 'Undertake post training assessment and provide follow-up and coaching', 'activity', '1222', None, [('W1',), ('W2',), ('W3',)]),
        ('1222.8', 'Hold awareness information dissemination sessions with regenerative agriculture groups on opportunities', 'activity', '1222', None, [('W1',), ('W2',), ('W3',)]),

        # Output 1223
        ('1223', 'Solar and improved technology solutions distributed to targeted women to reduce fuelwood harvesting, improve air quality, and reduce time poverty', 'output', '1220', None, None),
        ('1223.1', 'Train partners/participants on solar panels, cook stoves and associated kit operation and maintenance', 'activity', '1223', None, [('W2',), ('W3',)]),
        ('1223.2', 'Procure and distribute solar kits and solar panels', 'activity', '1223', None, [('W1',), ('W2',)]),
        ('1223.3', 'Procure and distribute fuel efficient cooking supplies', 'activity', '1223', None, [('W1',), ('W2',), ('W3',)]),

        # Immediate Outcome 1230
        ('1230', 'Increased capacity of community members and leaders, particularly men, to promote and support gender equality, women\'s rights and engagement in gender-responsive NbS with biodiversity co-benefit', 'immediate_outcome', '1200', None, None),

        # Output 1231
        ('1231', 'SBCC strategy to promote gender responsive NbS, economic rights & GE&I, including UPCW', 'output', '1230', None, None),
        ('1231.1', 'Conduct participatory design workshop to inform and design SBCC strategy to address gender responsive NbS, economic rights & GE&I, including UPCW', 'activity', '1231', None, [('Q1',)]),
        ('1231.2', 'Develop/adapt content for SBCC material', 'activity', '1231', None, [('Q1',)]),
        ('1231.3', 'Print material and produce media for SBCC strategy', 'activity', '1231', None, [('Q1',)]),
        ('1231.4', 'Implement SBCC strategy (launch, community fairs, murals, distribution of printed material, radio programs, banners)', 'activity', '1231', None, [('W1',), ('W2',), ('W3',)]),

        # Output 1232
        ('1232', 'Change Agents trained and supported to promote gender responsive NbS, economic rights & GE&I, including UPCW', 'output', '1230', None, None),
        ('1232.1', 'Map and identify potential Change Agents', 'activity', '1232', None, [('Q1',)]),
        ('1232.2', 'Develop/contextualize training material and information aids for Change Agents', 'activity', '1232', None, [('Q1',)]),
        ('1232.3', 'Train Change Agents', 'activity', '1232', None, [('W1',), ('W3', 'refresher')]),
        ('1232.4', 'Support Change Agents to develop community sensitization action plans', 'activity', '1232', None, [('Q1',)]),
        ('1232.5', 'Provide Change Agents with technical follow-up and materials for the implementation of their community sensitization action plans', 'activity', '1232', None, [('W1',), ('W2',), ('W3',)]),
        ('1232.6', 'Organize regional experience-sharing and learning exchanges for Change Agents', 'activity', '1232', None, [('W2',), ('W3',)]),
        ('1232.7', 'Organize inter-generational dialogues between YLOs and Change Agents', 'activity', '1232', None, [('W2',), ('W3',)]),

        # Output 1233
        ('1233', 'Men trained to promote and support gender responsive NbS, economic rights & GE&I, including UPCW', 'output', '1230', None, None),
        ('1233.1', 'Engage and recruit training participants as Male Champions', 'activity', '1233', None, [('Q1',)]),
        ('1233.2', 'Develop and adapt content for training, including retention strategy, to promote and support gender responsive NbS, economic rights & GE&I, including UPCW', 'activity', '1233', None, [('Q1',)]),
        ('1233.3', 'Provide ToT on training content', 'activity', '1233', None, [('Q1',)]),
        ('1233.4', 'Conduct trainings and provide coaching on content', 'activity', '1233', None, [('W1',), ('W2',), ('W3',)]),
        ('1233.5', 'Conduct post training coaching and mentoring sessions with trained groups', 'activity', '1233', None, [('W2',), ('W3',)]),

        # Output 1234
        ('1234', 'Inclusive gender-transformative household action plans developed and implemented in support of women\'s participation in gender responsive NbS (roles and responsibilities, decision making, access and control)', 'output', '1230', None, None),
        ('1234.1', 'Develop and adapt household action plan methodology and tools', 'activity', '1234', None, [('Q1',)]),
        ('1234.2', 'Provide ToT on household action plan methodology and tools', 'activity', '1234', None, [('W1',), ('W2',)]),
        ('1234.3', 'Facilitate the development of household action plans with targeted families', 'activity', '1234', None, [('W2',)]),
        ('1234.4', 'Monitor implementation of household action plans', 'activity', '1234', None, [('W2',), ('W3',)]),
        ('1234.5', 'Facilitate reflection and sharing between targeted households and communities', 'activity', '1234', None, [('W2',), ('W3',)]),

        # ── Intermediate Outcome 1300 ──
        ('1300', 'Improved gender-responsive and child/youth-friendly governance for climate adaptation, resilience and biodiversity', 'intermediate_outcome', None, None, None),

        # Immediate Outcome 1310
        ('1310', 'Increased awareness and knowledge of primary school children, particularly girls, on climate change, NbS, and conservation', 'immediate_outcome', '1300', None, None),

        # Output 1311
        ('1311', '4K and Roots and Shoots clubs established and trained on climate change, and conservation', 'output', '1310', None, None),
        ('1311.1', 'Conduct project sensitization to Ministry of Education, Teachers Service Commission (TSC) and schools to generate buy-in and sign agreements', 'activity', '1311', 'Completed', []),
        ('1311.2', 'Map existing 4K and Roots and Shoots school clubs', 'activity', '1311', 'Completed', []),
        ('1311.3', 'Establish new 4K and Roots and Shoots clubs where not existing', 'activity', '1311', None, [('Q1',)]),
        ('1311.4', 'Revise and contextualize training program material and methodology (4K Club, Climate Cards and Roots & Shoots)', 'activity', '1311', None, [('Q1',)]),
        ('1311.5', 'Train facilitators on program methodology and CP (school teachers, SMC members, BoM, Community Champions)', 'activity', '1311', None, [('Q1',)]),
        ('1311.6', 'Implement training program with groups', 'activity', '1311', None, [('W1',), ('W2',), ('W3', 'refresher')]),
        ('1311.7', 'Provide coaching, mentoring and supportive supervision to facilitators and BOMs', 'activity', '1311', None, [('W1',), ('W2',), ('W3',)]),

        # Output 1312
        ('1312', '4K and Roots and Shoots clubs supported to implement community based climate change, and conservation initiatives', 'output', '1310', None, None),
        ('1312.1', 'Support the development of community based climate change, and conservation initiatives by 4K and Roots and Shoots clubs', 'activity', '1312', None, [('W1',), ('W2',)]),
        ('1312.2', 'Provide material support for implementation for 4k and Roots and Shoots clubs (inputs and technical assistance)', 'activity', '1312', None, [('W1',), ('W2',)]),
        ('1312.3', 'Facilitate learning and sharing exchanges between 4K and Roots and Shoots clubs', 'activity', '1312', None, [('W2',), ('W3',)]),

        # Output 1313
        ('1313', 'Innovative clean water solution established in targeted schools', 'output', '1310', None, None),
        ('1313.1', 'Form and build capacity of school-based water management and maintenance clubs', 'activity', '1313', None, [('W1',), ('W2',)]),
        ('1313.2', 'Provide Solvatten kits in targeted schools', 'activity', '1313', None, [('Q1',)]),
        ('1313.3', 'Establish demonstration plots for drip-irrigation at target schools including management and maintenance committees', 'activity', '1313', None, [('W1',), ('W2',), ('W3',)]),
        ('1313.4', 'Provide rainwater harvesting and drip-irrigation solutions to targeted schools', 'activity', '1313', None, [('W2',)]),

        # Immediate Outcome 1320
        ('1320', 'Strengthened gender responsive community governance structures to reduce risk and enhance preparedness to climate change', 'immediate_outcome', '1300', None, None),

        # Output 1321
        ('1321', 'Community-level gender responsive adaptation and preparedness plans developed and funded', 'output', '1320', None, None),
        ('1321.1', 'Develop and adapt participatory risk assessment and planning tools and methodology', 'activity', '1321', None, [('W2',)]),
        ('1321.2', 'Train facilitators on participatory risk assessment and planning tools and methodology', 'activity', '1321', None, [('W2',)]),
        ('1321.3', 'Conduct participatory multi-hazard risk assessment in targeted communities', 'activity', '1321', None, [('W2',)]),
        ('1321.4', 'Analyze and summarize findings from multi-hazard risk assessment', 'activity', '1321', None, [('W2',)]),
        ('1321.5', 'Facilitate evidence based participatory planning with community stakeholders to develop gender responsive adaptation and preparedness plans', 'activity', '1321', None, [('W2',), ('W3',)]),
        ('1321.6', 'Provide material support for selected initiatives in community gender responsive adaptation and preparedness plans', 'activity', '1321', None, [('W2',), ('W3',)]),
        ('1321.7', 'Provide ongoing supportive supervision to the implementation of gender responsive adaptation and preparedness plans', 'activity', '1321', None, [('W2',), ('W3',)]),

        # Output 1322
        ('1322', 'Communities linked with county level and national climate, risk reduction and preparedness funds', 'output', '1320', None, None),
        ('1322.1', 'Map existing national and county climate, risk reduction and preparedness funding mechanisms and opportunities', 'activity', '1322', None, [('W2',)]),
        ('1322.2', 'Raise awareness to communities on appropriate existing funding mechanisms and opportunities', 'activity', '1322', None, [('W2',), ('W3',)]),
        ('1322.3', 'Support communities to access climate action funding through linkage meetings and support to develop funding applications', 'activity', '1322', None, [('W2',), ('W3',)]),

        # Output 1323
        ('1323', 'High-level event held in project counties, with global leaders, experts and innovators to profile and promote gender responsive NbS and increase Kenyan investment in locally led NbS', 'output', '1320', None, None),
        ('1323.1', 'Document knowledge and prepare materials for sharing/discussion', 'activity', '1323', None, [('W2',), ('W3',)]),
        ('1323.2', 'Hold high-level national learning and sharing event', 'activity', '1323', None, [('W3',)]),

        # Immediate Outcome 1330
        ('1330', 'Increased ability of WRO and YLOs to undertake evidenced-based advocacy for gender responsive and inclusive climate adaptation and resilience', 'immediate_outcome', '1300', None, None),

        # Output 1331
        ('1331', 'Evidence on benefits of gender responsive and inclusive climate adaptation and resilience generated through the project\'s M&E systems and specialized research', 'output', '1330', None, None),
        ('1331.1', 'Conduct Baseline, GBA+ (including referral services) and endline evaluation studies', 'activity', '1331', None, [('W1',), ('W2',), ('W3',)]),
        ('1331.2', 'Conduct rapid biodiversity and gendered climate risk assessment of target implementation areas', 'activity', '1331', None, [('Q1',)]),
        ('1331.3', 'Set up project Management Information System (MIS)', 'activity', '1331', None, [('Q1',)]),
        ('1331.4', 'Research business case for payment for ecosystem services', 'activity', '1331', None, [('W2',), ('W3',)]),
        ('1331.5', 'Conduct specialized research on the social, economic, climate and biodiversity benefits of Nature Based Solutions', 'activity', '1331', None, [('W2',), ('W3',)]),

        # Output 1332
        ('1332', 'Evidence on benefits of gender responsive and inclusive climate adaptation and resilience disseminated to communities, governments, research and academic institution', 'output', '1330', None, None),
        ('1332.1', 'Develop knowledge management and dissemination strategy', 'activity', '1332', None, [('Q1',)]),
        ('1332.2', 'Edit and print material as per audiences targeted in knowledge management strategy', 'activity', '1332', None, [('Q1',)]),
        ('1332.3', 'Distribute material to targeted audiences', 'activity', '1332', None, [('W1',), ('W3',)]),
        ('1332.4', 'Organize information sharing events on evidence benefits of NbS with targeted audiences', 'activity', '1332', None, [('W1',), ('W2',), ('W3',)]),

        # Output 1333
        ('1333', 'Members of WRO and YLOs trained on leadership, gender and climate change, and evidenced-based advocacy', 'output', '1330', None, None),
        ('1333.1', 'Conduct mapping of WRO and YLOs in the targeted area', 'activity', '1333', None, []),
        ('1333.2', 'Conduct capacity needs assessment of WROs and YLOs', 'activity', '1333', None, []),
        ('1333.3', 'Develop training package for WROs and YLOs on leadership, gender and climate change, and evidenced-based advocacy', 'activity', '1333', None, [('Q1',)]),
        ('1333.4', 'Deliver ToT on leadership, gender and climate change, and evidenced-based advocacy', 'activity', '1333', None, [('Q1',)]),
        ('1333.5', 'Train WRO and YLO members on leadership, gender and climate change, and evidenced-based advocacy', 'activity', '1333', None, [('W1',), ('W3', 'refresher')]),
        ('1333.6', 'Organize information sharing events on evidence benefits of NbS with WROs and YLOs', 'activity', '1333', None, [('W2',), ('W3',)]),

        # Output 1334
        ('1334', 'WRO and YLOs\' evidenced-based advocacy plans supported to increase action on gender responsive and inclusive climate adaptation and resilience', 'output', '1330', None, None),
        ('1334.1', 'Support WROs and YLOs on the development of evidenced-based advocacy plans', 'activity', '1334', None, [('Q1',)]),
        ('1334.2', 'Provide inputs to WROs and YLOs for the implementation of their evidence-based advocacy plans', 'activity', '1334', None, [('W2',)]),
        ('1334.3', 'Provide supportive supervision to WROs and YLOs during the implementation of their evidence-based advocacy plans', 'activity', '1334', None, [('W2',), ('W3',)]),
    ]

    # Build lookup maps
    int_out_map = {}
    imm_out_map = {}
    output_map = {}
    sort_counter = {'int': 0, 'imm': 0, 'out': 0, 'act': 0}

    for code, desc, entity_type, parent_code, status, flags in framework:
        if entity_type == 'intermediate_outcome':
            sort_counter['int'] += 1
            obj = IntermediateOutcome.query.filter_by(code=code).first()
            if not obj:
                obj = IntermediateOutcome(code=code, description=desc, sort_order=sort_counter['int'])
                db.session.add(obj)
                db.session.flush()
            int_out_map[code] = obj

        elif entity_type == 'immediate_outcome':
            sort_counter['imm'] += 1
            obj = ImmediateOutcome.query.filter_by(code=code).first()
            if not obj:
                parent = int_out_map[parent_code]
                obj = ImmediateOutcome(
                    code=code, description=desc,
                    intermediate_outcome_id=parent.id,
                    sort_order=sort_counter['imm']
                )
                db.session.add(obj)
                db.session.flush()
            imm_out_map[code] = obj

        elif entity_type == 'output':
            sort_counter['out'] += 1
            obj = Output.query.filter_by(code=code).first()
            if not obj:
                parent = imm_out_map[parent_code]
                obj = Output(
                    code=code, description=desc,
                    immediate_outcome_id=parent.id,
                    sort_order=sort_counter['out']
                )
                db.session.add(obj)
                db.session.flush()
            output_map[code] = obj

        elif entity_type == 'activity':
            sort_counter['act'] += 1
            obj = Activity.query.filter_by(code=code).first()
            if not obj:
                parent = output_map[parent_code]
                act_status = 'Completed' if status == 'Completed' else 'Active'
                obj = Activity(
                    code=code, description=desc,
                    output_id=parent.id,
                    status=act_status,
                    sort_order=sort_counter['act']
                )
                db.session.add(obj)
                db.session.flush()

            # Add schedule flags
            if flags:
                for flag_data in flags:
                    quarter = flag_data[0]
                    notes = flag_data[1] if len(flag_data) > 1 else None
                    existing = ScheduleFlag.query.filter_by(
                        activity_id=obj.id, quarter=quarter
                    ).first()
                    if not existing:
                        sf = ScheduleFlag(
                            activity_id=obj.id,
                            quarter=quarter,
                            is_planned=True,
                            notes=notes
                        )
                        db.session.add(sf)

    db.session.commit()
    print(f"Seeded: {sort_counter['int']} intermediate outcomes, "
          f"{sort_counter['imm']} immediate outcomes, "
          f"{sort_counter['out']} outputs, "
          f"{sort_counter['act']} activities")


def seed_all():
    """Run all seed functions."""
    print("Seeding roles and permissions...")
    role_map = seed_roles_and_permissions()
    print("Seeding budget holders...")
    seed_budget_holders()
    print("Seeding default admin...")
    seed_default_admin(role_map)
    print("Seeding results framework...")
    seed_results_framework()
    print("Seed complete!")
