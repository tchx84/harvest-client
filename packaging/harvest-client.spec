Name:           harvest-client 
Version:        0.2.0
Release:        1
Summary:        Client for the Harvest Project

License:        GPLv2+
URL:            https://github.com/tchx84/harvest-client
Source0:        %{name}-%{version}.tar.gz

Requires:       python >= 2.7

BuildArch:      noarch

%description
Client for the Harvest Project that aims to make learning visible to educators and decision makers

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/sugar/extensions/webservice/
cp -r extensions/webservice/harvest $RPM_BUILD_ROOT/%{_datadir}/sugar/extensions/webservice/

mkdir -p $RPM_BUILD_ROOT/%{_datadir}/sugar/extensions/cpsection/webaccount/services/
cp -r extensions/cpsection/webaccount/services/harvest $RPM_BUILD_ROOT/%{_datadir}/sugar/extensions/cpsection/webaccount/services/

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/NetworkManager/dispatcher.d
cp etc/harvest-collect-ifup $RPM_BUILD_ROOT/%{_sysconfdir}/NetworkManager/dispatcher.d

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{_datadir}/sugar/extensions/webservice/harvest/__init__.py
%{_datadir}/sugar/extensions/webservice/harvest/account.py
%{_datadir}/sugar/extensions/webservice/harvest/harvest/__init__.py
%{_datadir}/sugar/extensions/webservice/harvest/harvest/harvest_logger.py
%{_datadir}/sugar/extensions/webservice/harvest/harvest/errors.py
%{_datadir}/sugar/extensions/webservice/harvest/harvest/crop.py
%{_datadir}/sugar/extensions/webservice/harvest/harvest/harvest.py
%{_datadir}/sugar/extensions/cpsection/webaccount/services/harvest/__init__.py
%{_datadir}/sugar/extensions/cpsection/webaccount/services/harvest/service.py
%{_sysconfdir}/NetworkManager/dispatcher.d/harvest-collect-ifup

%changelog
* Sat Nov 9 2013 Martin Abente Lahaye <tch@sugarlabs.org>
- Include mime_type
- Higher selection probability
- Limit retries interval
- Send hashed serial number

*Thu Oct 24 2013 Martin Abente Lahaye <tch@sugarlabs.org>
- Initial RPM release
