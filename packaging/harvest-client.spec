Name:           harvest-client 
Version:        0.3.2
Release:        1
Summary:        Client for the Harvest Project

License:        GPLv2+
URL:            https://github.com/tchx84/harvest-client
Source0:        %{name}-%{version}.tar.gz

Requires:       python >= 2.7, sugar >= 0.100

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
* Tue Jun 17 2014 Martin Abente Lahaye <tch@sugarlabs.org>
- landed grades, times and traffic changes.

* Wed Feb 05 2014 Martin Abente Lahaye <tch@sugarlabs.org>
- Support not enabling automatic collection

* Fri Jan 24 2014 Martin Abente Lahaye <tch@sugarlabs.org>
- Check if serial, age and gender are present before collect

* Mon Jan 6 2014 Martin Abente Lahaye <tch@sugarlabs.org>
- Set URL and API-KEY non-editable

* Thu Dec 5 2013 Martin Abente Lahaye <tch@sugarlabs.org>
- Refactor and adjust logger coding style
- Ignore trigger when missing server
- Use random retry time
- Collect laptops data
- Save crops on failure and restore on retry
- Use libsoup instead of urllib2

* Sat Nov 9 2013 Martin Abente Lahaye <tch@sugarlabs.org>
- Include mime_type
- Higher selection probability
- Limit retries interval
- Send hashed serial number

*Thu Oct 24 2013 Martin Abente Lahaye <tch@sugarlabs.org>
- Initial RPM release
