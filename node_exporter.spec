%bcond check 1

%global goipath         github.com/prometheus/node_exporter
%global forgeurl        https://github.com/prometheus/node_exporter

Name:           node_exporter
Version:        1.10.2
Release:        1%{?dist}
Summary:        Prometheus exporter for hardware and OS metrics

License:        Apache-2.0
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/v%{version}/node_exporter-%{version}.tar.gz
Source1:        node_exporter-%{version}-vendor.tar.bz2
Source2:        go-vendor-tools.toml
Source3:        node_exporter.service
Source4:        node-exporter.xml

ExclusiveArch:  %{golang_arches_future}
BuildRequires:  go-rpm-macros
BuildRequires:  go-vendor-tools
BuildRequires:  systemd-rpm-macros
BuildRequires:  firewalld-filesystem
# Static BuildRequires for dynamic dependency (askalono-cli)
BuildRequires:  askalono-cli
Requires:       firewalld-filesystem
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
Prometheus exporter for hardware and OS metrics exposed by *NIX kernels,
written in Go with pluggable metric collectors.

%prep
%autosetup -p1 -n node_exporter-%{version}
tar -xf %{S:1}

%generate_buildrequires
%go_vendor_license_buildrequires -c %{S:2}

%build
%global gomodulesmode GO111MODULE=on
export GO_LDFLAGS="\
 -X github.com/prometheus/common/version.Version=%{version} \
 -X github.com/prometheus/common/version.Revision=%{release} \
 -X github.com/prometheus/common/version.Branch=tarball \
 -X github.com/prometheus/common/version.BuildDate=%(date -u +%%Y%%m%%d-%%H:%%M:%%S)"
%gobuild -o %{gobuilddir}/bin/node_exporter %{goipath}

%install
%go_vendor_license_install -c %{S:2}

install -Dpm 0755 %{gobuilddir}/bin/node_exporter %{buildroot}%{_bindir}/node_exporter

install -Dpm 0644 %{S:3} %{buildroot}%{_unitdir}/node_exporter.service
install -Dpm 0644 %{S:4} %{buildroot}%{_prefix}/lib/firewalld/services/node-exporter.xml

install -dm 0755 %{buildroot}%{_sysusersdir}
cat > %{buildroot}%{_sysusersdir}/node_exporter.conf <<'EOF'
u node_exporter - "Prometheus Node Exporter" /
EOF

%check
%go_vendor_license_check -c %{S:2}
%if %{with check}
%gocheck2
%endif

%pre
%sysusers_create_compat %{_sysusersdir}/node_exporter.conf

%post
%systemd_post node_exporter.service
%firewalld_reload

%preun
%systemd_preun node_exporter.service

%postun
%systemd_postun_with_restart node_exporter.service
%firewalld_reload

%files -f %{go_vendor_license_filelist}
%license LICENSE NOTICE
%doc README.md
%{_bindir}/node_exporter
%{_unitdir}/node_exporter.service
%{_prefix}/lib/firewalld/services/node-exporter.xml
%{_sysusersdir}/node_exporter.conf

%changelog
* Fri Mar 27 2026 KOSHIKAWA Kenichi <reishoku.gh@pm.me> - 1.10.2-1
- Initial package of node_exporter 1.10.2
