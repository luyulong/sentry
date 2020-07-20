import React from 'react';
import styled from '@emotion/styled';

import space from 'app/styles/space';
import {Team} from 'app/types';

type Props = Team;

const TeamCard = ({slug}: Props) => {
  return (
    <Wrapper>
      <Header>{slug}</Header>
    </Wrapper>
  );
};

export default TeamCard;

const Wrapper = styled('div')`
  background-color: ${p => p.theme.white};
  border: 1px solid ${p => p.theme.gray400};
  border-radius: ${p => p.theme.borderRadius};
  box-shadow: ${p => p.theme.dropShadowLight};
  padding: ${space(1)};
  @media (min-width: ${p => p.theme.breakpoints[0]}) {
    width: 50%;
  }
  @media (min-width: ${p => p.theme.breakpoints[1]}) {
    width: 33%;
  }
  @media (min-width: ${p => p.theme.breakpoints[2]}) {
    width: 25%;
  }
`;

const Header = styled('div')``;
