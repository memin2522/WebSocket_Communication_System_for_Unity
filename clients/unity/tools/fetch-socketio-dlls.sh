#!/usr/bin/env sh
# Descarga de NuGet las DLL del cliente Socket.IO (SocketIOClient 3.1.2) y sus
# dependencias, y las copia a Assets/Plugins/SocketIO/. Requiere el SDK de .NET.
# Las DLL no se versionan en el repositorio (ver .gitignore).
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HERE/../Assets/Plugins/SocketIO"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

cat > "$WORK/fetch.csproj" <<'XML'
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>netstandard2.1</TargetFramework>
    <CopyLocalLockFileAssemblies>true</CopyLocalLockFileAssemblies>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="SocketIOClient" Version="3.1.2" />
    <PackageReference Include="SocketIO.Serializer.NewtonsoftJson" Version="3.1.2" />
  </ItemGroup>
</Project>
XML

dotnet publish "$WORK/fetch.csproj" -c Release -o "$WORK/out" --nologo -v q
mkdir -p "$DEST"
find "$WORK/out" -name '*.dll' ! -name 'fetch.dll' -exec cp {} "$DEST/" \;
echo "DLL copiadas en $DEST:"
ls "$DEST"
