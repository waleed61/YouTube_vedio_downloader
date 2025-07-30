{ pkgs }: {
  deps = [
    pkgs.ffmpeg
    pkgs.python311
    pkgs.python311Packages.flask
    pkgs.python311Packages.yt-dlp
  ];
}
