%define _disable_ld_no_undefined	1
Name:		opensm
Version:	3.3.20
Release:	1
Summary:	OpenIB InfiniBand Subnet Manager and management utilities
License:	GPLv2 or BSD
Url:		http://www.openfabrics.org/
Source0:	http://www.openfabrics.org/downloads/management/%{name}-%{version}.tar.gz
Source2:	opensm.logrotate
Source4:	opensm.sysconfig
Source5:	opensm.service
Source6:	opensm.launch
Source7:	opensm.rwtab
Patch0:		opensm-3.3.17-prefix.patch

BuildRequires:		libibmad-devel
BuildRequires:		bison
BuildRequires:		byacc
BuildRequires:		bison
BuildRequires:		systemd
Requires:		%{name}-libs = %{version}-%{release},
Requires:		logrotate
Requires:		rdma
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd

%description
OpenSM is the OpenIB project's Subnet Manager for Infiniband networks.
The subnet manager is run as a system daemon on one of the machines in
the infiniband fabric to manage the fabric's routing state.  This package
also contains various tools for diagnosing and testing Infiniband networks
that can be used from any machine and do not need to be run on a machine
running the opensm daemon.

%files
%dir /var/cache/opensm
%{_sbindir}/*
%{_mandir}/*/*
%{_unitdir}/*
%{_libexecdir}/*
%config(noreplace) %{_sysconfdir}/logrotate.d/opensm
%config(noreplace) %{_sysconfdir}/rdma/opensm.conf
%config(noreplace) %{_sysconfdir}/sysconfig/opensm
%{_sysconfdir}/rwtab.d/opensm
%doc AUTHORS COPYING ChangeLog INSTALL README NEWS

#---------------------------------------------------------------------------

%package libs
Summary: Libraries used by opensm and included utilities

%description libs
Shared libraries for Infiniband user space access

%files libs
%{_libdir}/lib*.so.*

#---------------------------------------------------------------------------

%package devel
Summary: Development files for the opensm-libs libraries

Requires: %{name}-libs = %{version}-%{release}

%description devel
Development environment for the opensm libraries

%files devel
%{_libdir}/lib*.so
%{_includedir}/infiniband

#---------------------------------------------------------------------------

%prep
%setup -q
%autopatch -p1

%build
export CC=gcc
%configure --with-opensm-conf-sub-dir=rdma
%make_build
cd opensm
./opensm -c ../opensm-%{version}.conf

%install
%make_install
# remove unpackaged files from the buildroot
rm -f %{buildroot}%{_libdir}/*.la
rm -fr %{buildroot}%{_sysconfdir}/init.d
install -D -m644 opensm-%{version}.conf %{buildroot}%{_sysconfdir}/rdma/opensm.conf
install -D -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/opensm
install -D -m644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/opensm
install -D -m644 %{SOURCE5} %{buildroot}%{_unitdir}/opensm.service
install -D -m755 %{SOURCE6} %{buildroot}%{_libexecdir}/opensm-launch
install -D -m644 %{SOURCE7} %{buildroot}%{_sysconfdir}/rwtab.d/opensm
mkdir -p ${RPM_BUILD_ROOT}/var/cache/opensm

%post
%systemd_post opensm.service

%preun
# Don't use the macro because we need to remove our cache directory as well
# and the macro doesn't have the ability to do that.  But, here the macro
# is for future reference:
# %systemd_preun opensm.service
if [ $1 = 0 ]; then
	/bin/systemctl --no-reload disable opensm.service >/dev/null 2>&1 || :
	/bin/systemctl stop opensm.service >/dev/null 2>&1 || :
	rm -fr /var/cache/opensm
fi

%postun
%systemd_postun_with_restart opensm.service

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

