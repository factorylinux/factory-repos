Summary:        Factory package repositories
Name:           factory-repos
Version:        36
Release:        300%{?dist}
License:        MIT
URL:            https://factorylinux.com/

Provides:       factory-repos(%{version}) = %{release}
Requires:       system-release(%{version})
Obsoletes:      factory-repos < %{version}
Requires:       factory-gpg-keys >= %{version}-%{release}
BuildArch:      noarch
# Required by %%check
BuildRequires:  gnupg sed

Source1:        archmap
Source2:        factory.repo
Source3:        factory.conf
Source4:        RPM-GPG-KEY-factory-%{version}-primary

%description
Factory Linux package repository files for yum and dnf along with gpg public keys.


%package -n factory-gpg-keys
Summary:        Factory RPM keys

%description -n factory-gpg-keys
This package provides the RPM signature keys.


%package ostree
Summary:        OSTree specific files

%description ostree
This package provides ostree specfic files like remote config from
where client's system will pull OSTree updates.

%prep

%build

%install
# Install the keys
install -d -m 755 $RPM_BUILD_ROOT/etc/pki/rpm-gpg
install -m 644 %{_sourcedir}/RPM-GPG-KEY* $RPM_BUILD_ROOT/etc/pki/rpm-gpg/

# Link the primary/secondary keys to arch files, according to archmap.
pushd $RPM_BUILD_ROOT/etc/pki/rpm-gpg/

for keyfile in RPM-GPG-KEY*; do
    # resolve symlinks, so that we don't need to keep duplicate entries in archmap
    real_keyfile=$(basename $(readlink -f $keyfile))
    key=${real_keyfile#RPM-GPG-KEY-} # e.g. 'factory-36-primary'
    if ! grep -q "^${key}:" %{_sourcedir}/archmap; then
        echo "ERROR: no archmap entry for $key"
        exit 1
    fi
    arches=$(sed -ne "s/^${key}://p" %{_sourcedir}/archmap)
    for arch in $arches; do
        # replace last part with $arch (factory-36-primary -> factory-36-$arch)
        ln -s $keyfile ${keyfile%%-*}-$arch # NOTE: RPM replaces %% with %
    done
done
# and add symlink for compat generic location
ln -s RPM-GPG-KEY-factory-%{version}-primary RPM-GPG-KEY-%{version}-factory
popd

# Install repo files
install -d -m 755 $RPM_BUILD_ROOT/etc/yum.repos.d
for file in %{_sourcedir}/factory*repo ; do
  install -m 644 $file $RPM_BUILD_ROOT/etc/yum.repos.d
done

# Install ostree remote config
install -d -m 755 $RPM_BUILD_ROOT/etc/ostree/remotes.d/
install -m 644 %{_sourcedir}/factory.conf $RPM_BUILD_ROOT/etc/ostree/remotes.d/


%files
%dir /etc/yum.repos.d
%config(noreplace) /etc/yum.repos.d/factory.repo


%files -n factory-gpg-keys
%dir /etc/pki/rpm-gpg
/etc/pki/rpm-gpg/RPM-GPG-KEY-*


%files ostree
%dir /etc/ostree/remotes.d/
/etc/ostree/remotes.d/factory.conf


%changelog
* Thu Oct 20 2022 Factory Linux Developers <info@factorylinux.com> 
- Built For The Factory Linux!
