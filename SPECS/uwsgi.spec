%define wikiversion 25

Name:               uwsgi
Version:            0.9.9.2
Release:            4%{?dist}
Summary:            Fast, self-healing, application container server
Group:              System Environment/Daemons   
License:            GPLv2
URL:                http://projects.unbit.it/uwsgi
Source0:            http://projects.unbit.it/downloads/%{name}-%{version}.tar.gz
Source1:            fedora.ini
# wikiversion=25; curl -o uwsgi-wiki-doc-v${wikiversion}.txt "http://projects.unbit.it/uwsgi/wiki/Doc?version=${wikiversion}&format=txt"
Source2:            uwsgi-wiki-doc-v%{wikiversion}.txt
Source3:            uwsgi.init
Patch0:             uwsgi_fix_rpath.patch
Patch1:             uwsgi_trick_chroot_rpmbuild.patch
BuildRequires:      curl,  python-devel, libxml2-devel, libuuid-devel, jansson-devel
BuildRequires:      libyaml-devel, perl-devel, ruby-devel, perl-ExtUtils-Embed
BuildRequires:      python-greenlet-devel, lua-devel, ruby
BuildRequires:      python3-devel
Requires(pre):      shadow-utils
Requires(post):     /sbin/service
Requires(preun):    initscripts
Requires(postun):   /sbin/service

%description
uWSGI is a fast (pure C), self-healing, developer/sysadmin-friendly
application container server.  Born as a WSGI-only server, over time it has
evolved in a complete stack for networked/clustered web applications,
implementing message/object passing, caching, RPC and process management. 
It uses the uwsgi (all lowercase, already included by default in the Nginx
and Cherokee releases) protocol for all the networking/interprocess
communications.  Can be run in preforking mode, threaded,
asynchronous/evented and supports various form of green threads/coroutine
(like uGreen and Fiber).  Sysadmin will love it as it can be configured via
command line, environment variables, xml, .ini and yaml files and via LDAP. 
Being fully modular can use tons of different technology on top of the same
core.

%package -n %{name}-devel
Summary:  uWSGI - Development header files and libraries
Group:    Development/Libraries
Requires: %{name}

%description -n %{name}-devel
This package contains the development header files and libraries
for uWSGI extensions

%package -n %{name}-plugin-common
Summary:  uWSGI - Common plugins for uWSGI
Group:    System Environment/Daemons
Requires: %{name}

%description -n %{name}-plugin-common
This package contains the most common plugins used with uWSGI. The
plugins included in this package are: cache, cgi, rpc, ugreen

%package -n %{name}-plugin-rack
Summary:  uWSGI - Ruby rack plugin
Group:    System Environment/Daemons
Requires: rubygem-rack, %{name}-plugin-common

%description -n %{name}-plugin-rack
This package contains the rack plugin for uWSGI

%package -n %{name}-plugin-psgi
Summary:  uWSGI - Plugin for PSGI support
Group:    System Environment/Daemons
Requires: perl-PSGI, %{name}-plugin-common

%description -n %{name}-plugin-psgi
This package contains the psgi plugin for uWSGI

%package -n %{name}-plugin-python
Summary:  uWSGI - Plugin for Python support
Group:    System Environment/Daemons
Requires: python, %{name}-plugin-common

%description -n %{name}-plugin-python
This package contains the python plugin for uWSGI

%package -n %{name}-plugin-nagios
Summary:  uWSGI - Plugin for Nagios support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common

%description -n %{name}-plugin-nagios
This package contains the nagios plugin for uWSGI

%package -n %{name}-plugin-fastrouter
Summary:  uWSGI - Plugin for FastRouter support
Group:    System Environment/Daemons
Requires: %{name}-plugin-common

%description -n %{name}-plugin-fastrouter
This package contains the fastrouter (proxy) plugin for uWSGI

%package -n %{name}-plugin-admin
Summary:  uWSGI - Plugin for Admin support
Group:    System Environment/Daemons   
Requires: %{name}-plugin-common

%description -n %{name}-plugin-admin
This package contains the admin plugin for uWSGI

%package -n %{name}-plugin-python3
Summary:  uWSGI - Plugin for Python 3.2 support
Group:    System Environment/Daemons   
Requires: python3, %{name}-plugin-common

%description -n %{name}-plugin-python3
This package contains the Python 3.2 plugin for uWSGI

%package -n %{name}-plugin-ruby
Summary:  uWSGI - Plugin for Ruby support
Group:    System Environment/Daemons   
Requires: ruby, %{name}-plugin-common

%description -n %{name}-plugin-ruby
This package contains the Ruby 1.9 plugin for uWSGI

%package -n %{name}-plugin-greenlet
Summary:  uWSGI - Plugin for Python Greenlet support
Group:    System Environment/Daemons   
Requires: python-greenlet, %{name}-plugin-common

%description -n %{name}-plugin-greenlet
This package contains the python greenlet plugin for uWSGI

%package -n %{name}-plugin-lua
Summary:  uWSGI - Plugin for LUA support
Group:    System Environment/Daemons   
Requires: lua, %{name}-plugin-common

%description -n %{name}-plugin-lua
This package contains the lua plugin for uWSGI

%prep
%setup -q
cp -p %{SOURCE1} buildconf/
cp -p %{SOURCE2} uwsgi-wiki-doc-v%{wikiversion}.txt
sed -i 's/\r//' uwsgi-wiki-doc-v%{wikiversion}.txt
echo "plugin_dir = %{_libdir}/%{name}" >> buildconf/$(basename %{SOURCE1})
%patch0 -p1
%patch1 -p1

%build
CFLAGS="%{optflags} -Wno-unused-but-set-variable" python uwsgiconfig.py --build fedora.ini

%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_includedir}/%{name}
mkdir -p %{buildroot}%{_libdir}/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/run/%{name}
%{__install} -d -m 0755 %{buildroot}%{_initrddir}
%{__install} -p -m 0755 %{SOURCE3} %{buildroot}%{_initrddir}/%{name}
%{__install} -p -m 0755 uwsgi %{buildroot}%{_sbindir}
%{__install} -p -m 0644 *.h %{buildroot}%{_includedir}/%{name}
%{__install} -p -m 0644 *_plugin.so %{buildroot}%{_libdir}/%{name}

%pre
getent group uwsgi >/dev/null || groupadd -r uwsgi
getent passwd uwsgi >/dev/null || \
    useradd -r -g uwsgi -d '/etc/uwsgi' -s /sbin/nologin \
    -c "uWSGI Service User" uwsgi

%post
/sbin/chkconfig --add uwsgi

%preun
if [ $1 -eq 0 ]; then
    /sbin/service uwsgi stop >/dev/null 2>&1
    /sbin/chkconfig --del uwsgi

%postun
if [ $1 -ge 1 ]; then
    /sbin/service uwsgi condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root)
%dir %{_sysconfdir}/%{name}
%{_initrddir}/%{name}
%{_sbindir}/%{name}
%attr(0755,uwsgi,uwsgi) %{_localstatedir}/log/%{name}
%attr(0755,uwsgi,uwsgi) %{_localstatedir}/run/%{name}
%doc ChangeLog LICENSE README
%doc uwsgi-wiki-doc-v%{wikiversion}.txt

%files -n %{name}-devel
%{_includedir}/%{name}

%files -n %{name}-plugin-common
%{_libdir}/%{name}/cache_plugin.so
%{_libdir}/%{name}/cgi_plugin.so
%{_libdir}/%{name}/rpc_plugin.so
%{_libdir}/%{name}/ugreen_plugin.so

%files -n %{name}-plugin-rack
%{_libdir}/%{name}/rack_plugin.so

%files -n %{name}-plugin-psgi
%{_libdir}/%{name}/psgi_plugin.so

%files -n %{name}-plugin-python
%{_libdir}/%{name}/python_plugin.so

%files -n %{name}-plugin-nagios
%{_libdir}/%{name}/nagios_plugin.so

%files -n %{name}-plugin-fastrouter
%{_libdir}/%{name}/fastrouter_plugin.so

%files -n %{name}-plugin-admin
%{_libdir}/%{name}/admin_plugin.so

%files -n %{name}-plugin-python3
%{_libdir}/%{name}/python32_plugin.so

%files -n %{name}-plugin-ruby
%{_libdir}/%{name}/ruby19_plugin.so

%files -n %{name}-plugin-greenlet
%{_libdir}/%{name}/greenlet_plugin.so

%files -n %{name}-plugin-lua
%{_libdir}/%{name}/lua_plugin.so


%changelog
* Mon Oct 31 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9.2-4
- Add init script to manage instances
- Add uwsgi user and group

* Fri Oct 28 2011 Jeff Goldschrafe <jeff@holyhandgrenade.org> - 0.9.9.2-3
- Fork package from Jorge A Gallegos
- Bundle application state directories with package in preparation for init
  script bundling

* Sun Oct 09 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.2-2
- Don't download the wiki page at build time

* Sun Oct 09 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.9.2-1
- Updated to latest stable version
- Correctly linking plugin_dir
- Patches 1 and 2 were addressed upstream

* Sun Aug 21 2011 Jorge A Gallegos <kad@blegh.net> - 0.9.8.3-3
- Got rid of BuildRoot
- Got rid of defattr()

* Sun Aug 14 2011 Jorge Gallegos <kad@blegh.net> - 0.9.8.3-2
- Added uwsgi_fix_rpath.patch
- Backported json_loads patch to work with jansson 1.x and 2.x
- Deleted clean steps since they are not needed in fedora

* Sun Jul 24 2011 Jorge Gallegos <kad@blegh.net> - 0.9.8.3-1
- rebuilt
- Upgraded to latest stable version 0.9.8.3
- Split packages

* Sun Jul 17 2011 Jorge Gallegos <kad@blegh.net> - 0.9.6.8-2
- Heavily modified based on Oskari's work

* Mon Feb 28 2011 Oskari Saarenmaa <os@taisia.fi> - 0.9.6.8-1
- Initial.
