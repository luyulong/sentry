import React from 'react';
import {RouteComponentProps} from 'react-router/lib/Router';
import {Location} from 'history';

import {openCreateTeamModal} from 'app/actionCreators/modal';
import Button from 'app/components/button';
import {t} from 'app/locale';
import withOrganization from 'app/utils/withOrganization';
import SentryDocumentTitle from 'app/components/sentryDocumentTitle';
import PageHeading from 'app/components/pageHeading';
import {Organization, Team} from 'app/types';
import {IconAdd} from 'app/icons';
import ListLink from 'app/components/links/listLink';
import NavTabs from 'app/components/navTabs';
import recreateRoute from 'app/utils/recreateRoute';
import {PageContent, PageHeader} from 'app/styles/organization';
import withTeams from 'app/utils/withTeams';

import TeamCard from './teamCard';

type Props = RouteComponentProps<
  {orgId: string; projectId: string; location: Location},
  {}
> & {
  organization: Organization;
  location: Location;
  params: Record<string, string | undefined>;
  teams: Array<Team>;
};

const TeamsDashboard = ({organization, routes, location, params, teams}: Props) => {
  const access = new Set(organization.access);
  const canCreateTeams = access.has('project:admin');
  const displayMyTeams = location.pathname.endsWith('my-teams/');
  const baseUrl = recreateRoute('', {location, routes, params, stepBack: -1});
  const displayTeams = displayMyTeams ? teams.filter(team => team.isMember) : teams;

  const handleCreateTeam = () => {
    openCreateTeamModal({organization});
  };

  return (
    <React.Fragment>
      <SentryDocumentTitle title={t('Teams Dashboard')} objSlug={organization.slug} />
      <PageContent>
        <PageHeader>
          <PageHeading>{t('Teams')}</PageHeading>
          <Button
            size="small"
            disabled={!canCreateTeams}
            title={
              !canCreateTeams
                ? t('You do not have permission to create teams')
                : undefined
            }
            onClick={handleCreateTeam}
            icon={<IconAdd size="xs" isCircled />}
          >
            {t('Create Team')}
          </Button>
        </PageHeader>
        <NavTabs underlined>
          <ListLink to={baseUrl} index isActive={() => !displayMyTeams}>
            {t('All Teams')}
          </ListLink>
          <ListLink to={`${baseUrl}my-teams/`} isActive={() => displayMyTeams}>
            {t('My Teams')}
          </ListLink>
        </NavTabs>
        {displayTeams.map(displayTeam => (
          <TeamCard key={displayTeam.id} {...displayTeam} />
        ))}
      </PageContent>
    </React.Fragment>
  );
};

export default withOrganization(withTeams(TeamsDashboard));
